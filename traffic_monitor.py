from scapy.all import sniff
import logging
from datetime import datetime
import os
import json

#TODO: move conn_attempts to its own file as a json obj
conn_attempts = {}

LOG_FILE = 'traffic.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

def get_timestamps():
    timestamp = datetime.now().strftime('%Y-%m-%d %H-:%M:%S')
    timestamp_arr = str(datetime.now()).split(' ')[1].split(':')
    secTime = float(timestamp_arr[2]) + int(timestamp_arr[1])*60 + int(timestamp_arr[0])*3600

    return timestamp, secTime


def log_packet(packet):
    try:
        timestamp, secTime = get_timestamps()

        src_ip = packet[0][1].src
        dst_ip = packet[0][1].dst
        src_port = packet[0][2].sport
        dst_port = packet[0][2].dport

        log_entry = f'[{timestamp}] Traffic: {src_ip}:{src_port} -> {dst_ip}:{dst_port}'
        print(log_entry)
        logging.info(log_entry)

        log_key = (src_ip)
        if log_key not in conn_attempts:
            conn_attempts[log_key] = [conn_attempts.get(log_key, 0) + 1, secTime]
        elif log_key in conn_attempts and conn_attempts[secTime - log_key][1] < 5:
            conn_attempts[log_key][0] += 1
            logging.warning(f'consecutive attempts')
        else:
            conn_attempts[log_key][0] += 1
        
        print()
        print(conn_attempts)
        print()
    

    except Exception as e:
        logging.error(f'Error processing packet: {e}')

def start_sniffing():
    print('Starting packet sniffing on port 9999...')
    sniff(filter='tcp', prn=log_packet, store=False)

if __name__ == '__main__':
    start_sniffing()