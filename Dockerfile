FROM python:3.9-slim
WORKDIR /webapp
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y redis-server
EXPOSE 7860 6379
RUN chmod +x /webapp/start.sh
# CMD ["/webapp/start.sh"]
# CMD ["newrelic-admin", "run-program", "/webapp/start.sh"]
CMD ["/bin/sh", "/webapp/start.sh"]
