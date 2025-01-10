from datetime import datetime
from collections import deque
from scapy.all import sniff
import logging
import socket
import json
import os
import mysql.connector
import sql_config


def get_ip():
    """ Get the ip address of this machine. """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception as e:
        return f'Error: {e}'


IP=get_ip()
CONN_ATTEMPT_THRESHOLD=150 # the maximum number of connection requests that can be made from an ip address
TIMESTAMP_LIFETIME=1 # number of seconds until a timestamp is removed from the CONN_ATTEMPTS_FILE
LOG_FILE='traffic.log' # log file where network traffic is dumped
CONN_ATTEMPTS_FILE="connection_attempts.json" # json object that tracks connection attempts from different ip addrs

# Info to connect to the local MySQL database
db_config = {
    'host': sql_config.DB_HOST,
    'user': sql_config.DB_USER,
    'password': sql_config.DB_PASSWORD,
    'database': sql_config.DB_NAME
}

# set config of the log file
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')


def get_timestamps():
    """ Get the current timestamp. Note timestamp_val is a datetime object. """
    timestamp_val = datetime.now()
    timestamp_str = timestamp_val.strftime('%Y-%m-%d %H:%M:%S.%f')

    return timestamp_str, timestamp_val


def update_prev_conn_attempts(cur_time_str, cur_time_val, prev_attempts):
    """
    Add the current connection attempt to the array of previous attempts. Then delete all the old connection attempts,
    and if the the number of attempts is still greater than the the threshold return False. return True otherwise.
    Also return the updated prev_attempts array.
    """
    give_warning = False
    prev_attempts.append(cur_time_str)
    first_timestamp = datetime.strptime(prev_attempts[0], "%Y-%m-%d %H:%M:%S.%f")
    
    # clear out all old timestamps
    while len(prev_attempts) > 0:
        time_delta = cur_time_val - first_timestamp
        if time_delta.total_seconds() < TIMESTAMP_LIFETIME:
            break
        prev_attempts.popleft()
    
    if len(prev_attempts) > CONN_ATTEMPT_THRESHOLD:
        give_warning = True
    
    return list(prev_attempts), give_warning, len(prev_attempts)


def insert_log_entry(conn, cursor, timestamp, source_ip, source_port, dest_ip, dest_port):
    insert_query = """
    INSERT INTO traffic_logs (timestamp, source_ip, source_port, dest_ip, dest_port)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (timestamp, source_ip, source_port, dest_ip, dest_port))
    conn.commit()

def log_packet(packet):
    try:

        # Get data to record the packet
        timestamp_str, timestamp_val = get_timestamps()
        src_ip = packet[0][1].src
        dst_ip = packet[0][1].dst
        src_port = packet[0][2].sport
        dst_port = packet[0][2].dport
        if dst_ip != IP:
            return

        log_entry = f'[{timestamp_str}] Traffic: {src_ip}:{src_port} -> {dst_ip}:{dst_port}'
        print(log_entry)

        # add the log_entry to the traffic.log file
        logging.info(log_entry)

        # insert the log entry into the database
        insert_log_entry(conn, cursor, timestamp_str, src_ip, src_port, dst_ip, dst_port)

        # Update the connection_attempts object with the new packet
        give_warning = False
        conn_attempts_obj = {}
        if os.path.exists(CONN_ATTEMPTS_FILE):
            # load the current conn_attempts_obj
            with open(CONN_ATTEMPTS_FILE, 'r') as file:
                conn_attempts_obj = json.load(file)

        # update the obj with the new log
        if src_ip not in conn_attempts_obj:
            conn_attempts_obj[src_ip] = [0, [timestamp_str]]
        else:
            conn_attempts_obj[src_ip][0] = conn_attempts_obj[src_ip][0]+1
            prev_attempts = deque(conn_attempts_obj[src_ip][1])
            new_attempts, give_warning, num_attempts = update_prev_conn_attempts(timestamp_str, timestamp_val, prev_attempts)
            conn_attempts_obj[src_ip][1] = new_attempts
            
        with open(CONN_ATTEMPTS_FILE, 'w') as file:
            json.dump(conn_attempts_obj, file)

        # Log a warning if the source has sent a suspicious amount of traffic
        if give_warning:
            logging.warning(f'WARNING: ip {src_ip} has sent {num_attempts} connection requests in the past {TIMESTAMP_LIFETIME} seconds')    

    except Exception as e:
        logging.error(f'Error processing packet: {e}')


def start_sniffing():
    """ Record tcp traffic as it comes into this machine. """
    print('Starting packet sniffing')
    sniff(filter='tcp', prn=log_packet, store=False)


if __name__ == '__main__':
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        start_sniffing()
    except mysql.connector.Error as e:
        print(f'Error: {e}')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print('MySQL connection closed.')
