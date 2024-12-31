import socket
import time

SERVER_IP = '10.0.2.4'
SERVER_PORT = 9999
NUM_ATTEMPTS = 10
DELAY = 0.1

def attempt_connections():
    for attempt in range(NUM_ATTEMPTS):
        try:
            print(f'Attempt {attempt+1}/{NUM_ATTEMPTS} to connect to {SERVER_IP}:{SERVER_PORT}...\n')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((SERVER_IP, SERVER_PORT))
                print(f"Successfully connected on attempt {attempt}")
        except Exception as e:
            print(f'Attempt {attempt} failed: {e}')
        time.sleep(DELAY)

if __name__ == "__main__":
    attempt_connections()