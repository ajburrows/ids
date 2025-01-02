from scapy.all import sniff
import logging
from datetime import datetime
import os
import json
from collections import deque
import netifaces
import socket

def get_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception as e:
        return f'Error: {e}'

CONN_ATTEMPT_THRESHOLD = 2
LOG_FILE = 'traffic.log'
CONN_ATTEMPTS_FILE = "connection_attempts.json"
IP=get_ip()
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

def get_timestamps():
    timestamp_val = datetime.now()
    timestamp_str = timestamp_val.strftime('%Y-%m-%d %H-:%M:%S')

    return timestamp_str, timestamp_val




def log_packet(packet):
    try:
        timestamp_str, timestamp_val = get_timestamps()

        src_ip = packet[0][1].src
        dst_ip = packet[0][1].dst
        src_port = packet[0][2].sport
        dst_port = packet[0][2].dport

        if dst_ip != IP:
            return

        log_entry = f'[{timestamp_str}] Traffic: {src_ip}:{src_port} -> {dst_ip}:{dst_port}'
        print(log_entry)
        logging.info(log_entry)

        give_warning = False
        conn_attempts_obj = {}
        if os.path.exists(CONN_ATTEMPTS_FILE):
            # load the current conn_attempts_obj
            with open(CONN_ATTEMPTS_FILE, 'r') as file:
                conn_attempts_obj = json.load(file)

        # up date the obj with the new log
        if src_ip not in conn_attempts_obj:
            conn_attempts_obj[src_ip] = [0, [str(timestamp_val)]]
        else:
            conn_attempts_obj[src_ip][0] = conn_attempts_obj[src_ip][0]+1
            prev_attempts = deque(conn_attempts_obj[src_ip][1])
            prev_attempts.append(str(timestamp_val))
            while len(prev_attempts) > CONN_ATTEMPT_THRESHOLD:
                prev_attempts.popleft()
                give_warning = True
            conn_attempts_obj[src_ip][1] = list(prev_attempts)

            
        with open(CONN_ATTEMPTS_FILE, 'w') as file:
            json.dump(conn_attempts_obj, file)

        if give_warning:
            logging.warning(f'WARNING: ip {src_ip} has sent more than {CONN_ATTEMPT_THRESHOLD} connection requests')    

    except Exception as e:
        logging.error(f'Error processing packet: {e}')

def start_sniffing():
    print('Starting packet sniffing on port 9999...')
    sniff(filter='tcp', prn=log_packet, store=False)

if __name__ == '__main__':
    start_sniffing()