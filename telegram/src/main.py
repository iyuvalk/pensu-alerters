import os
import datetime
import time
from kafka import KafkaConsumer
import telepot as telepot
import re
from telepot.loop import MessageLoop

alert_message_template = '''
The following anomaly was detected regarding metric ${metric}:
- htm_anomaly_score: ${htm_anomaly_score}
- htm_anomaly_likelihood: ${htm_anomaly_likelihood}
- anomaly_score: ${anomaly_score}
- prediction: ${prediction}
- value: ${value}
- timestamp: ${timestamp}
'''


class PensuAlerter:
    def __validate_env_vars(self):
        PENSU_ALERTER_TELEGRAM_BOT_ID = os.environ.get('PENSU_ALERTER_TELEGRAM_BOT_ID', None)
        PENSU_ALERTER_TELEGRAM_BOT_SECRET = os.environ.get('PENSU_ALERTER_TELEGRAM_BOT_SECRET', None)
        PENSU_ALERTER_TELEGRAM_ALERTS_TOPIC = os.environ.get('PENSU_ALERTER_TELEGRAM_ALERTS_TOPIC', None)
        PENSU_ALERTER_TELEGRAM_KAFKA_SERVER = os.environ.get('PENSU_ALERTER_TELEGRAM_KAFKA_SERVER', None)
        PENSU_ALERTER_TELEGRAM_KAFKA_CLIENT_ID = os.environ.get('PENSU_ALERTER_TELEGRAM_KAFKA_CLIENT_ID', None)
        PENSU_ALERTER_TELEGRAM_KAFKA_SESSION_TIMEOUT = os.environ.get('PENSU_ALERTER_TELEGRAM_KAFKA_SESSION_TIMEOUT', None)
        if PENSU_ALERTER_TELEGRAM_BOT_ID is None or \
                PENSU_ALERTER_TELEGRAM_BOT_SECRET is None or \
                PENSU_ALERTER_TELEGRAM_ALERTS_TOPIC is None or \
                PENSU_ALERTER_TELEGRAM_KAFKA_SERVER is None or \
                PENSU_ALERTER_TELEGRAM_KAFKA_CLIENT_ID is None or \
                PENSU_ALERTER_TELEGRAM_KAFKA_SESSION_TIMEOUT is None:
            raise Exception('All the following environment variables must be set: PENSU_ALERTER_TELEGRAM_BOT_ID, PENSU_ALERTER_TELEGRAM_BOT_SECRET, PENSU_ALERTER_TELEGRAM_KAFKA_SERVER, PENSU_ALERTER_TELEGRAM_KAFKA_CLIENT_ID, PENSU_ALERTER_TELEGRAM_ALERTS_TOPIC, PENSU_ALERTER_TELEGRAM_KAFKA_SESSION_TIMEOUT')

    def __init__(self):
        self.__validate_env_vars()
        bot_id = os.environ.get('PENSU_ALERTER_TELEGRAM_BOT_ID')
        bot_secret = os.environ.get('PENSU_ALERTER_TELEGRAM_BOT_SECRET')
        bot_creds = bot_id + ":" + bot_secret
        self._bot = telepot.Bot(bot_creds)
        self._kafka_consumer = KafkaConsumer(os.environ.get('PENSU_ALERTER_TELEGRAM_ALERTS_TOPIC'),
               bootstrap_servers=os.environ.get('PENSU_ALERTER_TELEGRAM_KAFKA_SERVER'),
               client_id=os.environ.get('PENSU_ALERTER_TELEGRAM_KAFKA_CLIENT_ID'),
               consumer_timeout_ms=float(os.environ.get('PENSU_ALERTER_TELEGRAM_KAFKA_SESSION_TIMEOUT')))

    def __prepare_message__(self, alert_info):
        alert_report_id = alert_info.get('report_id', "<NONE>")
        alert_metric_name = alert_info.get('metric', "<NONE>")
        alert_metadata = alert_info.get('meta_data', None)
        result = alert_info.replace("${alert_report_id}", str(alert_report_id))
        result = result.replace("${metric}", str(alert_metric_name))
        result = result.replace("${htm_anomaly_score}", str(alert_metadata.get('htm_anomaly_score', "<NONE>")))
        result = result.replace("${htm_anomaly_likelihood}", str(alert_metadata.get('htm_anomaly_likelihood', "<NONE>")))
        result = result.replace("${anomaly_score}", str(alert_metadata.get('anomaly_score', "<NONE>")))
        result = result.replace("${timestamp}", str(alert_metadata.get('timestamp', "<NONE>")))
        result = result.replace("${prediction}", str(alert_metadata.get('prediction', "<NONE>")))
        result = result.replace("${value}", str(alert_metadata.get('value', "<NONE>")))
        return result

    def bot_commands_responder(self, msg):
        chat_id = msg['chat']['id']
        command = msg['text']

        if command == '/chat_id':
            self._bot.sendMessage(chat_id, str(chat_id))
        elif command == '/time':
            self._bot.sendMessage(chat_id, str(datetime.datetime.now()))
        else:
            print("[CHAT_ID:" + str(chat_id) + "][WARN]: Received the following unrecognized command " + command)

    def run(self):
        send_to_chat_id = os.environ.get('PENSU_ALERTER_TELEGRAM_CHAT_ID')
        MessageLoop(self._bot, self.bot_commands_responder).run_as_thread()

        while True:
            try:
                for alert_info in self._kafka_consumer:
                    self._bot.sendMessage(send_to_chat_id, self.__prepare_message__(alert_info))
            except Exception as ex:
                print("[CHAT_ID:-------][WARN]: Could not connect to kafka. Will sleep for 10 seconds and will retry. "
                      "(Exception: " + str(ex) + ")")
                time.sleep(10)
            print("[CHAT_ID:-------][INFO]: No alerts from kafka. Going to take a nap for 1 second")
            time.sleep(1)


PensuAlerter().run()
