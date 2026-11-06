import numpy as np
import pandas as pd
import string
from unidecode import unidecode
from collections import Counter


class TextPreprocessor:
    def __init__(self, remove_punct: bool = True, remove_digits: bool = True,
                 remove_stop_words: bool = True,
                 remove_short_words: bool = False, minlen: int = 1, maxlen: int = 1, top_p: float = None,
                 bottom_p: float = None):
        self.remove_punct = remove_punct
        self.remove_digits = remove_digits
        self.remove_stop_words = remove_stop_words
        self.remove_short_words = remove_short_words
        self.minlen = minlen
        self.maxlen = maxlen
        self.top_p = top_p
        self.bottom_p = bottom_p
        self.words_to_remove = []
        self.stop_words = ["'d", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
 'about',
 'above',
 'across',
 'after',
 'afterwards',
 'again',
 'against',
 'ain',
 'all',
 'almost',
 'alone',
 'along',
 'already',
 'also',
 'although',
 'always',
 'am',
 'among',
 'amongst',
 'amount',
 'an',
 'and',
 'another',
 'any',
 'anyhow',
 'anyone',
 'anything',
 'anyway',
 'anywhere',
 'are',
 'around',
 'as',
 'at',
 'back',
 'be',
 'became',
 'because',
 'become',
 'becomes',
 'becoming',
 'been',
 'before',
 'beforehand',
 'behind',
 'being',
 'below',
 'beside',
 'besides',
 'between',
 'beyond',
 'both',
 'bottom',
 'but',
 'by',
 'ca',
 'call',
 'can',
 'cannot',
 'could',
 'couldn',
 "couldn't",
 'd',
 'did',
 'do',
 'does',
 'doing',
 'done',
 'down',
 'due',
 'during',
 'each',
 'eight',
 'either',
 'eleven',
 'else',
 'elsewhere',
 'empty',
 'enough',
 'even',
 'ever',
 'every',
 'everyone',
 'everything',
 'everywhere',
 'except',
 'few',
 'fifteen',
 'fifty',
 'first',
 'five',
 'for',
 'former',
 'formerly',
 'forty',
 'four',
 'from',
 'front',
 'full',
 'further',
 'get',
 'give',
 'go',
 'had',
 'has',
 'have',
 'having',
 'he',
 'hence',
 'her',
 'here',
 'hereafter',
 'hereby',
 'herein',
 'hereupon',
 'hers',
 'herself',
 'him',
 'himself',
 'his',
 'how',
 'however',
 'hundred',
 'i',
 'if',
 'in',
 'indeed',
 'into',
 'is',
 'it',
 "it's",
 'its',
 'itself',
 'just',
 'keep',
 'last',
 'latter',
 'latterly',
 'least',
 'less',
 'll',
 'm',
 'ma',
 'made',
 'make',
 'many',
'say',
'said',
'says',
'told',
'tell',
 'may',
 'me',
 'meanwhile',
 'might',
 'mine',
 'more',
 'moreover',
 'most',
 'mostly',
 'move',
 'much',
 'must',
 'my',
 'myself',
 'name',
 'namely',
 'neither',
 'never',
 'nevertheless',
 'next',
 'nine',
 'no',
 'nobody',
 'none',
 'noone',
 'nor',
 'not',
 'nothing',
 'now',
 'nowhere',
 'o',
 'of',
 'off',
 'often',
 'on',
 'once',
 'one',
 'only',
 'onto',
 'or',
 'other',
 'others',
 'otherwise',
 'our',
 'ours',
 'ourselves',
 'out',
 'over',
 'own',
 'part',
 'per',
 'perhaps',
 'please',
 'put',
 'quite',
 'rather',
 're',
'rs',
 'really',
 'regarding',
 's',
 'same',
 'say',
 'see',
 'seem',
 'seemed',
 'seeming',
 'seems',
 'serious',
 'several',
 'shan',
 "shan't",
 'she',
 "she's",
 'should',
 "should've",
 'shouldn',
 "shouldn't",
 'show',
 'side',
 'since',
 'six',
 'sixty',
 'so',
 'some',
 'somehow',
 'someone',
 'something',
 'sometime',
 'sometimes',
 'somewhere',
 'still',
 'such',
 't',
 'take',
 'ten',
 'than',
 'that',
 "that'll",
 'the',
 'their',
 'theirs',
 'them',
 'themselves',
 'then',
 'thence',
 'there',
 'thereafter',
 'thereby',
 'therefore',
 'therein',
 'thereupon',
 'these',
 'they',
 'third',
 'this',
 'those',
 'though',
 'three',
 'through',
 'throughout',
 'thru',
 'thus',
 'to',
 'together',
 'too',
 'top',
 'toward',
 'towards',
 'twelve',
 'twenty',
 'two',
 'under',
 'unless',
 'until',
 'up',
 'upon',
 'us',
 'used',
 'using',
 'various',
 've',
 'very',
 'via',
 'was',
 'wasn',
 "wasn't",
 'we',
 'well',
 'were',
 'weren',
 "weren't",
 'what',
 'whatever',
 'when',
 'whence',
 'whenever',
 'where',
 'whereafter',
 'whereas',
 'whereby',
 'wherein',
 'whereupon',
 'wherever',
 'whether',
 'which',
 'while',
 'whither',
 'who',
 'whoever',
 'whole',
 'whom',
 'whose',
 'why',
 'will',
 'with',
 'within',
 'without',
 'won',
 "won't",
 'would',
 'wouldn',
 "wouldn't",
 'y',
 'yet',
 'you',
 "you'd",
 "you'll",
 "you're",
 "you've",
 'your',
 'yours',
 'yourself',
 'yourselves',
 '‘d',
 '‘ll',
 '‘m',
 '‘re',
 '‘s',
 '‘ve',
 '’d',
 '’ll',
 '’m',
 '’re',
'new',
'old',
 '’s',
 '’ve']

        self.contraction_to_expansion = {"ain't": "am not",
                                         "aren't": "are not",
                                         "can't": "cannot",
                                         "can't've": "cannot have",
                                         "'cause": "because",
                                         "could've": "could have",
                                         "couldn't": "could not",
                                         "couldn't've": "could not have",
                                         "didn't": "did not",
                                         "doesn't": "does not",
                                         "don't": "do not",
                                         "hadn't": "had not",
                                         "hadn't've": "had not have",
                                         "hasn't": "has not",
                                         "haven't": "have not",
                                         "he'd": "he would",
                                         "he'd've": "he would have",
                                         "he'll": "he will",
                                         "he'll've": "he will have",
                                         "he's": "he is",
                                         "how'd": "how did",
                                         "how'd'y": "how do you",
                                         "how'll": "how will",
                                         "how's": "how is",
                                         "i'd": "i would",
                                         "i'd've": "i would have",
                                         "i'll": "i will",
                                         "i'll've": "i will have",
                                         "i'm": "i am",
                                         "i've": "i have",
                                         "isn't": "is not",
                                         "it'd": "it had",
                                         "it'd've": "it would have",
                                         "it'll": "it will",
                                         "it'll've": "it will have",
                                         "it's": "it is",
                                         "let's": "let us",
                                         "ma'am": "madam",
                                         "mayn't": "may not",
                                         "might've": "might have",
                                         "mightn't": "might not",
                                         "mightn't've": "might not have",
                                         "must've": "must have",
                                         "mustn't": "must not",
                                         "mustn't've": "must not have",
                                         "needn't": "need not",
                                         "needn't've": "need not have",
                                         "o'clock": "of the clock",
                                         "oughtn't": "ought not",
                                         "oughtn't've": "ought not have",
                                         "shan't": "shall not",
                                         "sha'n't": "shall not",
                                         "shan't've": "shall not have",
                                         "she'd": "she would",
                                         "she'd've": "she would have",
                                         "she'll": "she will",
                                         "she'll've": "she will have",
                                         "she's": "she is",
                                         "should've": "should have",
                                         "shouldn't": "should not",
                                         "shouldn't've": "should not have",
                                         "so've": "so have",
                                         "so's": "so is",
                                         "that'd": "that would",
                                         "that'd've": "that would have",
                                         "that's": "that is",
                                         "there'd": "there had",
                                         "there'd've": "there would have",
                                         "there's": "there is",
                                         "they'd": "they would",
                                         "they'd've": "they would have",
                                         "they'll": "they will",
                                         "they'll've": "they will have",
                                         "they're": "they are",
                                         "they've": "they have",
                                         "to've": "to have",
                                         "wasn't": "was not",
                                         "we'd": "we had",
                                         "we'd've": "we would have",
                                         "we'll": "we will",
                                         "we'll've": "we will have",
                                         "we're": "we are",
                                         "we've": "we have",
                                         "weren't": "were not",
                                         "what'll": "what will",
                                         "what'll've": "what will have",
                                         "what're": "what are",
                                         "what's": "what is",
                                         "what've": "what have",
                                         "when's": "when is",
                                         "when've": "when have",
                                         "where'd": "where did",
                                         "where's": "where is",
                                         "where've": "where have",
                                         "who'll": "who will",
                                         "who'll've": "who will have",
                                         "who's": "who is",
                                         "who've": "who have",
                                         "why's": "why is",
                                         "why've": "why have",
                                         "will've": "will have",
                                         "won't": "will not",
                                         "won't've": "will not have",
                                         "would've": "would have",
                                         "wouldn't": "would not",
                                         "wouldn't've": "would not have",
                                         "y'all": "you all",
                                         "y'alls": "you alls",
                                         "y'all'd": "you all would",
                                         "y'all'd've": "you all would have",
                                         "y'all're": "you all are",
                                         "y'all've": "you all have",
                                         "you'd": "you had",
                                         "you'd've": "you would have",
                                         "you'll": "you you will",
                                         "you'll've": "you you will have",
                                         "you're": "you are",
                                         "you've": "you have"
                                         }

    @staticmethod
    def __remove_double_whitespaces(string: str):
        return " ".join(string.split())

    async def __remove_url(self, string_series: pd.Series):
        """
        Removes URLs m text
        :param string_series: pd.Series, input string series
        :return: pd.Series, cleaned string series
        """
        clean_string_series = string_series.str.replace(
            pat=r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})",
            repl=" ", regex=True).copy()
        return clean_string_series.map(self.__remove_double_whitespaces)

    async def __expand(self, string_series: pd.Series):
        """
        Replaces contractions with expansions. eg. don't wit do not.
        :param string_series: pd.Series, input string series
        :return: pd.Series, cleaned string series
        """
        clean_string_series = string_series.copy()
        for c, e in self.contraction_to_expansion.items():
            clean_string_series = clean_string_series.str.replace(pat=c, repl=e, regex=False).copy()
        return clean_string_series.map(self.__remove_double_whitespaces)

    async def __remove_punct(self, string_series: pd.Series):
        """
       Removes punctuations from the input string.
       :param string_series: pd.Series, input string series
       :return: pd.Series, cleaned string series
       """
        clean_string_series = string_series.copy()
        puncts = [r'\n', r'\r', r'\t']
        puncts.extend(list(string.punctuation))
        for i in puncts:
            clean_string_series = clean_string_series.str.replace(pat=i, repl=" ", regex=False).copy()
        return clean_string_series.map(self.__remove_double_whitespaces)

    async def __remove_digits(self, string_series: pd.Series):
        """
       Removes digits from the input string.
       :param string_series: pd.Series, input string series
       :return: pd.Series, cleaned string series
       """
        clean_string_series = string_series.str.replace(pat=r'\d', repl=" ", regex=True).copy()
        return clean_string_series.map(self.__remove_double_whitespaces)

    @staticmethod
    async def __remove_short_words(string_series: pd.Series, minlen: int = 1, maxlen: int = 1):
        """
        Reomves words/tokens where minlen <= len <= maxlen.
        :param string_series: pd.Series, input string series
        :param minlen: int, minimum length of token to be removed.
        :param maxlen:  int, maximum length of token to be removed.
        :return: pd.Series, cleaned string series
        """
        clean_string_series = string_series.map(lambda string: " ".join([word for word in string.split() if
                                                                         (len(word) > maxlen) or (len(word) < minlen)]))
        return clean_string_series

    async def __remove_stop_words(self, string_series: pd.Series):
        """
       Removes stop words from the input string.
       :param string_series: pd.Series, input string series
       :return: pd.Series, cleaned string series
       """
        def str_remove_stop_words(string: str):
            stops = self.stop_words
            return " ".join([token for token in string.split() if token not in stops])

        return string_series.map(str_remove_stop_words)

    async def __remove_top_bottom_words(self, string_series: pd.Series, top_p: int = None,
                                  bottom_p: int = None, dataset: str = 'train'):
        """
        Reomoves top_p percent (frequent) words and bottom_p percent (rare) words.
        :param string_series: pd.Series, input string series
        :param top_p: float, percent of frequent words to remove.
        :param bottom_p: float, percent of rare words to remove.
        :param dataset: str, "train" for training set, "tesrt" for val/dev/test set.
        :return: pd.Series, cleaned string series
        """
        if dataset == 'train':
            if top_p is None:
                top_p = 0
            if bottom_p is None:
                bottom_p = 0

            if top_p > 0 or bottom_p > 0:
                word_freq = pd.Series(" ".join(string_series).split()).value_counts()
                n_words = len(word_freq)

            if top_p > 0:
                self.words_to_remove.extend([*word_freq.index[: int(np.ceil(top_p * n_words))]])

            if bottom_p > 0:
                self.words_to_remove.extend([*word_freq.index[-int(np.ceil(bottom_p * n_words)):]])

        if len(self.words_to_remove) == 0:
            return string_series
        else:
            clean_string_series = string_series.map(lambda string: " ".join([word for word in string.split()
                                                                             if word not in self.words_to_remove]))
            return clean_string_series

    async def preprocess(self, string_series: pd.Series, dataset: str = "train"):
        """
        Entry point.
        :param string_series: pd.Series, input string series
        :param dataset: str, "train" for training set, "tesrt" for val/dev/test set.
        :return: pd.Series, cleaned string series
        """
        string_series = string_series.str.lower().copy()
        string_series = string_series.map(unidecode).copy()
        string_series = await self.__remove_url(string_series=string_series)
        string_series = await self.__expand(string_series=string_series)

        if self.remove_punct:
            string_series = await self.__remove_punct(string_series=string_series)
        if self.remove_digits:
            string_series = await self.__remove_digits(string_series=string_series)
        if self.remove_stop_words:
            string_series = await self.__remove_stop_words(string_series=string_series)
        if self.remove_short_words:
            string_series = await self.__remove_short_words(string_series=string_series,
                                                      minlen=self.minlen,
                                                      maxlen=self.maxlen)
        string_series = await self.__remove_top_bottom_words(string_series=string_series,
                                                       top_p=self.top_p,
                                                       bottom_p=self.bottom_p, dataset=dataset)

        string_series = string_series.str.strip().copy()
        string_series.replace(to_replace="", value="this is an empty message", inplace=True)

        return string_series


async def get_frequent_words_html(df):
    text_preprocess = TextPreprocessor()
    preprocessed_txt = await text_preprocess.preprocess(df['title'] + ' ' + df['description'])
    counter = Counter(' '.join([*preprocessed_txt]).split())
    
    freq_tokens_html = '<div class="word-cloud-container">'
    n = 1
    for i, j in counter.most_common(25):
        freq_tokens_html += f'<a class="wc-tokens" onclick=wc_search("{i}")>{i}</a>{"&nbsp;" * np.random.randint(3, 7, 1)[0]}'
        if n == 5:
            freq_tokens_html += '<div class="word-cloud-section" id="word-cloud-section-id">'
        n += 1
    freq_tokens_html += '</div></div>'
    return freq_tokens_html