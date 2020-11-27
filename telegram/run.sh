#!/bin/bash
FILE=$(realpath "$0")
FOLDER=$(dirname "$FILE")
METRICS_COLLECTOR_DIR=$(dirname "$FOLDER")
FILENAME=$(basename "$FILE")

#export PENSU_ALERTER_TELEGRAM_BOT_ID=
#export PENSU_ALERTER_TELEGRAM_BOT_SECRET=

if [ -z "$PENSU_ALERTER_TELEGRAM_BOT_ID" ] || [ -z "$PENSU_ALERTER_TELEGRAM_BOT_SECRET" ]; then
  echo "ERROR: A telegram bot must be created first and its ID and secret mus be set as environment variables in this script"
  exit 9
fi

docker stack deploy pensu-alerter --compose-file "$FOLDER/docker-compose/docker-compose.yml"
while true; do
  "$METRICS_COLLECTOR_DIR/collect-metrics.py" | nc localhost 5555
done