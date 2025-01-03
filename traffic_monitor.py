from datetime import datetime
from collections import deque
from scapy.all import sniff
import logging
import socket
import json
import os


def get_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception as e:
        return f'Error: {e}'


CONN_ATTEMPT_THRESHOLD=2
LOG_FILE='traffic.log'
CONN_ATTEMPTS_FILE="connection_attempts.json"
IP=get_ip()
TIMESTAMP_LIFETIME=5
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')


def get_timestamps():
    timestamp_val = datetime.now()
    timestamp_str = timestamp_val.strftime('%Y-%m-%d %H:%M:%f')

    return timestamp_str, timestamp_val


def update_prev_conn_attempts(cur_time_str, cur_time_val, prev_attempts):
    """
    Add the current connection attempt to the array of previous attempts. Then delete all the old connection attempts,
    and if the the number of attempts is still greater than the the threshold return False. return True otherwise.
    Also return the updated prev_attempts array.
    """
    give_warning = False
    prev_attempts.append(cur_time_str)
    first_timestamp = datetime.strptime(prev_attempts[0], "%Y-%m-%d %H:%M:%f")
    print(f'cur_time_val: {cur_time_val}')
    print(f'first_timestamp: {first_timestamp}')
    while int(cur_time_val - first_timestamp) >= TIMESTAMP_LIFETIME:
        prev_attempts.popleft()
        datetime.strptime(prev_attempts[0], "%Y-%m-%d %H:%M:%f")
    
    if len(prev_attempts) > CONN_ATTEMPT_THRESHOLD:
        give_warning = True
    
    return list(prev_attempts), give_warning


def log_packet(packet):
    #try:
    timestamp_str, timestamp_val = get_timestamps()

    src_ip = packet[0][1].src
    dst_ip = packet[0][1].dst
    src_port = packet[0][2].sport
    dst_port = packet[0][2].dport

    if dst_ip != IP or src_port == 443:
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
        conn_attempts_obj[src_ip] = [0, [timestamp_str]]
    else:
        conn_attempts_obj[src_ip][0] = conn_attempts_obj[src_ip][0]+1
        prev_attempts = deque(conn_attempts_obj[src_ip][1])
        new_attempts, give_warning = update_prev_conn_attempts(timestamp_str, timestamp_val, prev_attempts)
        conn_attempts_obj[src_ip][1] = new_attempts
        
    with open(CONN_ATTEMPTS_FILE, 'w') as file:
        json.dump(conn_attempts_obj, file)

    if give_warning:
        logging.warning(f'WARNING: ip {src_ip} has sent more than {CONN_ATTEMPT_THRESHOLD} connection requests')    

    #except Exception as e:
    #    logging.error(f'Error processing packet: {e}')

def start_sniffing():
    print('Starting packet sniffing on port 9999...')
    sniff(filter='tcp', prn=log_packet, store=False)

if __name__ == '__main__':
    start_sniffing()