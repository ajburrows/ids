import socket
from datetime import datetime

HOST = '0.0.0.0'
PORT = 9999
LOG_FILE = 'connection_attempts.log'

def log_connection(address, port):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'[{timestamp}] Connection attempt from {address}:{port}\n'

    print(log_entry.strip())
    
    with open(LOG_FILE, 'a') as file:
        file.write(log_entry)
    
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f'Server listening on {HOST}:{PORT}...\n')
        
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                log_connection(client_address[0], client_address[1])

                client_socket.close()
            except KeyboardInterrupt:
                print("\nShutting down server.")
                break
            except Exception as e:
                print(f'Error: {e}')

if __name__ == "__main__":
    start_server()