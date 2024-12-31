import socket

HOST = '0.0.0.0'
PORT = 9999

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f'Server listening on {HOST}:{PORT}...\n')

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                message = "Hello from server!"
                client_socket.sendall(message.encode('utf-8'))
                client_socket.close()

            except KeyboardInterrupt:
                print('Shutting down server...\n')
                break

            except Exception as e:
                print(f'Error: {e}')

if __name__ == '__main__':
    start_server()
