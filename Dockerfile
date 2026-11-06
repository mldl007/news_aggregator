FROM python:3.9-slim

WORKDIR /webapp

COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN apt-get update \
    && apt-get install -y redis-server redis-tools \
    && rm -rf /var/lib/apt/lists/*

RUN printf '%s\n' \
    '#!/bin/sh' \
    'set -e' \
    'echo "Starting Redis..."' \
    'redis-server --daemonize yes --protected-mode yes --bind 127.0.0.1 --port 6379 --save "" --appendonly no' \
    'echo "Waiting for Redis..."' \
    'until redis-cli -h 127.0.0.1 -p 6379 ping 2>/dev/null | grep -q PONG; do sleep 1; done' \
    'echo "Redis is ready!"' \
    'redis-cli config set stop-writes-on-bgsave-error no' \
    'echo "Starting Gunicorn..."' \
    'exec newrelic-admin run-program gunicorn -b 0.0.0.0:${PORT:-7860} --timeout 120 --worker-class uvicorn.workers.UvicornWorker --workers 1 --threads 5 app:app' \
    > /webapp/start-render.sh \
    && chmod +x /webapp/start-render.sh

EXPOSE 7860 6379

CMD ["/bin/sh", "/webapp/start-render.sh"]
