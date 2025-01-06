import socket
import os

HOST = '10.0.2.15'
PORT = 443
PASSWORD = 'pass'
DATA_FILE = os.path.join(os.path.dirname(__file__), 'server_data.txt')

def handle_admin(admin_socket):
    pass

def handle_client(client_socket):
    client_socket.send(b'You have connected to the server. What would you like to do? (get data / login / exit)\n')
    logged_in = False

    while True:
        user_input = client_socket.recv(1024).decode().strip().lower()

        if user_input == 'get data':
            try:
                with open(DATA_FILE, 'r') as file:
                    data = file.read()
                    client_socket.send(f'Data:\n{data}\n'.encode())
                    break
            except FileNotFoundError:
                client_socket.close()
                client_socket.send(b'Error: data file not found.\n')
        elif user_input == 'login':
            client_socket.send(b'Enter password: ')
            password_input = client_socket.recv(1024).decode().strip()

            if password_input == PASSWORD:
                client_socket.send(b'Login successful. You can now use the "edit" command.\n')
                logged_in = True
                break
            else:
                client_socket.send(b'Incorrect password.\n')
        elif user_input == 'exit':
            break
        else:
            client_socket.send(b'Invalid command. Try again.\n')
        
    if logged_in:
        handle_admin(client_socket)

    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f'Server is listening on {HOST}:{PORT}')

    while True:
        client_socket, addr = server.accept()
        print(f'Accepted connection from {addr}')
        handle_client(client_socket)

if __name__ == '__main__':
    main()
