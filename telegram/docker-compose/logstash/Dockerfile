FROM docker.elastic.co/logstash/logstash:7.10.0
RUN bin/logstash-plugin install logstash-output-statsd
CMD logstash -f /etc/logstash/conf.d/logstash.conf