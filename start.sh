#!/bin/bash
redis-server --daemonize yes
redis-cli config set save ""
redis-cli config set appendonly no
redis-cli config set stop-writes-on-bgsave-error no
gunicorn -b 0.0.0.0:7860 --timeout 120 --worker-class uvicorn.workers.UvicornWorker --workers 5 --threads 5 app:app