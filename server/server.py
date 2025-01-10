import socket
import os

HOST = '10.0.2.15'
PORT = 443
PASSWORD = 'pass'
DATA_FILE = os.path.join(os.path.dirname(__file__), 'server_data.txt')
SERVER_RUNNING = True


def read_data():
    """ return the data stored in the DATA_FILE """
    try:
        data = ''
        with open(DATA_FILE, 'r') as file:
            data = file.read()
        return data
    except FileNotFoundError:
        print('Error: data file does not exist.\n')
    
def handle_admin(admin_socket):
    """ Handle commands with admin level privileges """
    while True:
        admin_socket.send(b'Enter a command (edit / get data / exit / shut down): ')
        user_input = admin_socket.recv(1024).decode().strip().lower()
        admin_socket.send(b'\n')

        # change the DATA_FILE conents to whatever the user enters. (There is no input checking)
        if user_input == 'edit':
            admin_socket.send(b'Enter new server data:\n')
            new_data = admin_socket.recv(1024).decode().strip()
            admin_socket.send(b'\n')

            with open(DATA_FILE, 'w') as file:
                file.write(new_data)
            admin_socket.send(b'Data updated.\n')
        
        # send the contents of the DATA_FILE to the client
        elif user_input == 'get data':
            data = read_data()
            admin_socket.send(f'Data:\n{data}\n\n'.encode())

        # disconnect fromt the client
        elif user_input == 'exit':
            break

        # shut the server down so no one can connect
        elif user_input == 'shut down':
            global SERVER_RUNNING
            SERVER_RUNNING = False
            break

        else:
            admin_socket.send(b'Invalid command. Try again.\n')

def handle_client(client_socket):
    """ Handle commands with client-level privileges """
    client_socket.send(b'You have connected to the server.\nEnter a command (get data / login / exit): ')
    logged_in = False

    while True:
        user_input = client_socket.recv(1024).decode().strip().lower()
        client_socket.send(b'\n')

        # send data from the DATA_FILE
        if user_input == 'get data':
            data = read_data()
            client_socket.send(f'Data:\n{data}\n\n'.encode())
            break

        # Switch to admin privileges if the password is correct
        elif user_input == 'login':
            client_socket.send(b'Enter password: ')
            password_input = client_socket.recv(1024).decode().strip()
            client_socket.send(b'\n')

            if password_input == PASSWORD:
                client_socket.send(b'Login successful. You can now use the "edit" command.\n')
                logged_in = True
                break
            else:
                client_socket.send(b'Incorrect password.\n')

        # disconnect from the client
        elif user_input == 'exit':
            break

        else:
            client_socket.send(b'Invalid command. Try again.\n')
        
    if logged_in:
        handle_admin(client_socket)

    client_socket.close()

def main():
    # open up the server socket to listen for client connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f'Server is listening on {HOST}:{PORT}')

    # handle commands from clients when they connect
    try:
        while SERVER_RUNNING:
            client_socket, addr = server.accept()
            print(f'Accepted connection from {addr}')
            handle_client(client_socket)
            print(f'while down. running? {SERVER_RUNNING}')
    except KeyboardInterrupt:
        print(f'Error: Keyboard interrupt')
    finally:    
        print('Closing server...')
        server.close()

if __name__ == '__main__':
    main()
