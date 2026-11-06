#!/bin/sh

set -e

echo "================================" echo "Starting Redis..." echo "================================"

redis-server
--daemonize yes
--protected-mode yes
--bind 127.0.0.1
--port 6379
--save ""
--appendonly no

echo "Waiting for Redis..."

until redis-cli -h 127.0.0.1 -p 6379 ping 2>/dev/null | grep -q PONG do sleep 1 done

echo "Redis is ready!"

redis-cli config set stop-writes-on-bgsave-error no

echo "================================" echo "Starting Gunicorn..." echo "================================"

exec newrelic-admin run-program gunicorn
-b 0.0.0.0:${PORT:-7860}
--timeout 120
--worker-class uvicorn.workers.UvicornWorker
--workers 1
--threads 5
app:app
