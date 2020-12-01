#!/usr/bin/python3

import sys
import re
import time
import psutil
import socket


def print_help():
    print('USAGE: collect-metrics.py --bootstrap-servers=<kafka_server:kafka_port> --metrics-topic=<kafka_topic_for_incoming_metrics>')
    print()
    print('This tool will collect some metrics from your computer and from the web and publish them to your kafka '
          'server for your Pensu instances to analyze. This will test the pensu alerter configured in the docker '
          'compose file you have loaded from this repo')


def parse_args(args):
    result = {}
    for arg in args:
        if re.match('^--help$', arg) or re.match('^-h$', arg) or re.match('^-\?$', arg):
            print_help()
            exit()

    return result


def get_metrics():
    hostname = socket.gethostname()
    metrics = {
        hostname + '.performance.cpu': psutil.cpu_percent(),
        hostname + '.performance.memory': psutil.virtual_memory().percent
    }

    partitions = psutil.disk_partitions()
    disk_counters_number = 0
    for partition in partitions:
        if disk_counters_number > 2:
            break
        if re.match('/dev/nvme.*', partition.device) or re.match('/dev/sd[abcd].*', partition.device):
            metrics[hostname + '.performance.disk.read_count' + partition.device.replace('/', '.')] = psutil.disk_io_counters().read_count
            metrics[hostname + '.performance.disk.write_count' + partition.device.replace('/', '.')] = psutil.disk_io_counters().write_count
            disk_counters_number = disk_counters_number + 1

    nics_data = psutil.net_io_counters(pernic=True)
    for nic in nics_data.keys():
        if re.match('en[a-z][0-9]', nic) or re.match('eth[0-9]', nic) or re.match('wl[a-z][0-9]', nic):
            metrics[hostname + '.performance.network.' + nic + '.bytes_sent'] = nics_data[nic].bytes_sent
            metrics[hostname + '.performance.network.' + nic + '.bytes_recv'] = nics_data[nic].bytes_recv

    temperature_sensors = psutil.sensors_temperatures()
    for key in temperature_sensors.keys():
        if len(temperature_sensors[key]) > 1:
            for sub_key in range(1, len(temperature_sensors[key])):
                metrics[hostname + '.temperature.' + key + '.' + temperature_sensors[key][sub_key].label] = temperature_sensors[key][sub_key].current
        else:
            metrics[hostname + '.temperature.' + key] = temperature_sensors[key][0].current
    return metrics


def main():
    parsed_args = parse_args(sys.argv)
    while True:
        metrics = get_metrics()
        for metric_name in metrics.keys():
            metric = metric_name + ' ' + str(metrics[metric_name]) + ' ' + str(int(time.time()))
            print(metric)
        time.sleep(5)

main()
