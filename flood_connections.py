import socket
import time

SERVER_IP = '10.0.2.4'
STARTING_PORT = 9990
NUM_ATTEMPTS = 10
DELAY = 0.1

# attempt to rapidly connect to various ports on the given ip address.
def attempt_connections():
    for attempt in range(NUM_ATTEMPTS):
        try:
            print(f'Attempt {attempt+1}/{NUM_ATTEMPTS} to connect to {SERVER_IP}:{STARTING_PORT+attempt}...\n')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((SERVER_IP, STARTING_PORT+attempt))
                print(f"Successfully connected on attempt {attempt+1}")
        except Exception as e:
            print(f'Attempt {attempt+1} failed: {e}')
        time.sleep(DELAY)

if __name__ == "__main__":
    print("NOTE: it is better to simply use nmap instead of flood_connections.py")
    attempt_connections()