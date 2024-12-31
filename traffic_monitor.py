from scapy.all import sniff
import logging
from datetime import datetime

LOG_FILE = 'traffic_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

def log_packet(packet):
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H-:%M:%S')

        src_ip = packet[0][1].src
        dst_ip = packet[0][1].dst
        src_port = packet[0][2].sport
        dst_port = packet[0][2].dport

        if dst_port == 9999:
            log_entry = f'[{timestamp}] Traffic: {src_ip}:{src_port} -> {dst_ip}:{dst_port}'
            print(log_entry)
            logging.info(log_entry)
    
    except Exception as e:
        logging.error(f'Error processing packet: {e}')

def start_sniffing():
    print('Starting packet sniffing on port 9999...')
    sniff(filter='tcp port 9999', prn=log_packet, store=False)

if __name__ == '__main__':
    start_sniffing()