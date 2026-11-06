import numpy as np
import pandas as pd
from dateutil import parser
from quart_cors import cors
from quart import Quart
from quart import render_template
from db_operations.db_operations import DBOperations
import logging
import traceback 
import redis
import uuid
from datetime import datetime
from functools import lru_cache
import gc
from word_cloud import get_frequent_words_html
from config import NEWS_RETENTION_SECONDS, UK_EDITION_URL


app = Quart(__name__)
app = cors(app, allow_origin="*")
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
logging.warning(f'Is Redis available?: {redis_client.ping()}') 
db = DBOperations()
session_id = None


REFRESH_FREQ = 300 # 300 secs = 5 mins

def is_db_fetch_reqd():
    try:
        env_news_time = redis_client.get('NEWSFETCHTIME')
        logging.warning(f'[session_id: {session_id}] fetch_time_env_var: {env_news_time}')
        fetch_flag = 1
        if env_news_time is None:
            redis_client.set("NEWSFETCHTIME", str(datetime.now()))
            fetch_flag = 1
    
        if env_news_time is not None:
            fetch_time_lapse_seconds = (datetime.now() - datetime.strptime(env_news_time, '%Y-%m-%d %H:%M:%S.%f')).seconds
            if fetch_time_lapse_seconds <= REFRESH_FREQ: 
                fetch_flag = 0 
            else:
                redis_client.set("NEWSFETCHTIME", str(datetime.now()))
                fetch_flag = 1
    except Exception as e:
        print(e)
        fetch_flag = 1
    return fetch_flag


def correct_date(x):
    if (not isinstance(x, str)) or (str(x).find(":") == -1):
        logging.error(f'[session_id: {session_id}] correct_date() error: {x} is not the right date format')
        return "2020-11-07 00:36:44+05:30"
    return x

def date_time_parser(dt):
    """
    Computes the minutes elapsed since published time.
    :param dt: date
    :return: int, minutes elapsed.
    """
    try:
        return int(np.round((dt.now(dt.tz) - dt).total_seconds() / 60, 0))
    except:
        logging.error(f'[session_id: {session_id}] date_time_parser() error: {dt} is not the right date format')
        return 100000


def elapsed_time_str(mins):
    """
    Return the time elapsed string from minutes passed as an argument.
    :param mins: int, minutes elapsed.
    :return: str, time elapsed string
    """
    try:
        time_str = ''
        hours = int(mins / 60)
        days = np.round(mins / (60 * 24), 1)
        remaining_mins = int(mins - (hours * 60))
        if days >= 1:
            time_str = f'{str(days)} days ago'
            if days == 1:
                time_str = 'a day ago'
        elif (days < 1) & (hours < 24) & (mins >= 60):
            time_str = f'{str(hours)} hours and {str(remaining_mins)} mins ago'
            if (hours == 1) & (remaining_mins > 1):
                time_str = f'an hour and {str(remaining_mins)} mins ago'
            if (hours == 1) & (remaining_mins == 1):
                time_str = f'an hour and a min ago'
            if (hours > 1) & (remaining_mins == 1):
                time_str = f'{str(hours)} hours and a min ago'
            if (hours > 1) & (remaining_mins == 0):
                time_str = f'{str(hours)} hours ago'
            if ((mins / 60) == 1) & (remaining_mins == 0):
                time_str = 'an hour ago'
        elif (days < 1) & (hours < 24) & (mins == 0):
            time_str = 'Just in'
        else:
            time_str = f'{str(mins)} minutes ago'
            if mins == 1:
                time_str = 'a minute ago'
        return time_str
    except:
        return "-"



async def fetch_from_db(fetch_flag):
    try:
        logging.warning(f'[session_id: {session_id}] fetch_flag: {fetch_flag}')
        if fetch_flag == 1:
            final_df = await db.read_news_from_db()
            freq_tokens = await get_frequent_words_html(final_df)
            logging.warning(f'[session_id: {session_id}] Fetched From DB')

            final_df['_id'] = final_df['_id'].astype('str')
            
            redis_client.set("NEWSDF", final_df.to_json())
            redis_client.set("NEWSWORDCLOUD", freq_tokens)
        else:
            final_df = pd.read_json(redis_client.get("NEWSDF"))
            freq_tokens = redis_client.get("NEWSWORDCLOUD")
            logging.warning(f'[session_id: {session_id}] Fetched From Cache')
            
    except Exception as e:
        print(e)
        final_df = []
        freq_tokens = ""
        raise
    return final_df, freq_tokens


@app.route("/")
async def index():
    """
    Entry point
    """
    try:
        global session_id
        session_id = uuid.uuid4().hex
        src_str = ''
        status_code = 200
        logging.warning(f'[session_id: {session_id}] Entering the application')
        final_df, freq_tokens = await fetch_from_db(is_db_fetch_reqd())
        if len(final_df) > 1:
            
            final_df["parsed_date"] = [correct_date(date_) for date_ in final_df['parsed_date']]
            final_df["parsed_date"] = [parser.parse(date_) for date_ in final_df['parsed_date']]
            final_df["elapsed_time"] =[date_time_parser(date_) for date_ in final_df['parsed_date']]
            final_df = final_df.loc[final_df["elapsed_time"] <= NEWS_RETENTION_SECONDS, :].copy()
            final_df["elapsed_time_str"] = final_df["elapsed_time"].apply(elapsed_time_str)
            final_df.sort_values(by="elapsed_time", inplace=True)
            src_str = ", ".join(sorted([*final_df['src'].unique()]))
            final_df['src_time'] = final_df['src'] + ("&nbsp;" * 5) + final_df["elapsed_time_str"]
            final_df.drop(columns=['_id', 'parsed_date', 'src', 'elapsed_time', 'elapsed_time_str'], inplace=True)
            final_df.drop_duplicates(subset='description', inplace=True)
            final_df = final_df.loc[(final_df["title"] != ""), :].copy()
        else:
            final_df = pd.DataFrame({'title': '', 'url': '',
                                     'description': '', 'src_time': ''}, index=[0])
        
    except Exception as e:
        final_df = pd.DataFrame({'title': '', 'url': '',
                                 'description': '', 'src_time': ''}, index=[0])
        logging.error(f'[session_id: {session_id}] {traceback.print_exc()}')

    result_str = f'''
                    <div class="box" id="main">
                    <form> 
                    
                    <div class="banner">
                    <img src="../static/favicon_new.png" class="logo-img" alt="KSV Muralidhar" />
                    <h1 style="display:inline-block; vertical-align: middle;">Latest Indian News</h1>
                    </div>
                 '''
    
    if len(final_df) <= 1:
        result_str += f'''<div><p class="unavailable">This app is temporarily unavailable</p></div>'''
        status_code = 500
    else:
        last_update_utc = datetime.strptime(redis_client.get('NEWSFETCHTIME'), '%Y-%m-%d %H:%M:%S.%f')
        last_update_mins = int(np.ceil((datetime.now() - last_update_utc).seconds / 60))
        last_update_str = f'Updated {last_update_mins} {"minutes" if last_update_mins > 1 else "minute"} ago'
        result_str += f'<p class="srctxt">News aggregated from <b>{src_str}</b>.<br><br>{last_update_str}&nbsp;&nbsp;&nbsp;&nbsp;<a href="{UK_EDITION_URL}"><b>Switch to UK edition</b></a></p>'

        result_str += '''
    	<div class="input-container">
		<input type="text" class="keyword-input" id="keywordInput" placeholder="Search" oninput="filterContent(true)">
		<div class="clear-btn" id="clearBtn" onclick="clearFilter()">&times;</div>
        <img src="static/info.png" alt="info" width="18" height="18" align="center" onclick="showSearchInfo()" style="cursor: pointer;">
		</div>
      '''

        result_str += f"{freq_tokens} "
        result_str += '<div class="show-more-word-cloud" onclick=word_cloud_display()><p class="three-dots">...</p></div>'

        result_str += f'''<div style="padding-bottom: 6px; font-size: 12px; font-family: Arial, Helvetica, sans-serif;">
                         News categories and similar news are AI-generated</div>
                         <div style="padding-bottom: 10px; font-size: 12px; font-family: Arial, Helvetica, sans-serif; font-weight: bold;">
                         {len(final_df)} news articles available</div>
                         '''

        
        for n, i in final_df.iterrows():  # iterating through the search results
            href = i["url"]
            category = i["category"]
            description = i["description"]
            url_txt = i["title"]
            src_time = i["src_time"]
            sim_news = i['similar_news']
            result_str += f'''<div class="news-item"><div style="padding-top: 7px;">
                              <a href="{href}" target="_blank" class="article-category">{category}
                              </a>
                              </div>
                              <div>
                              <a href="{href}" target="_blank" class="headline">{url_txt}
                              </a>
                              </div>
                              <div>
                              <a href="{href}" target="_blank" class="description">
                              {description}
                              </a>
                              </div>
                              <div>
                              <a href="{href}" target="_blank" class="time">
                              {src_time}
                               </a>
                               </div>


                                <div class="container">
                               <div class="content" style="display: none;">
                               {sim_news}
                               </div>
                               <div class="show-similar-button-container">
                               <button type="button" class="show-more">Show similar news</button>
								<button type="button" class="show-less">Hide similar news</button>
								</div>
                                </div>


                               
                               <div>
                               <p></p>
                               </div></div>
                               '''

    result_str += '</form></div>'
    logging.warning(f'[session_id: {session_id}] Successfully rendered template')
    gc.collect()
    return await render_template("index.html", body=result_str), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, workers=5, threads=5) # workers=(2*ncores) + 1, threads= (2 to 4*ncores) + 1
    
