# Importar módulo de socket

from socket import *
import os
from dotenv import load_dotenv
import threading
import signal

serverSocket = None

load_dotenv()
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))

MAX_ROOMS = 10 # Número máximo de salas

# Estruturas de dados para armazenar informações sobre a aplicação

clients = {} # {client_socket: {username: '', room: ''}}
rooms = {} # {room_name: [client_socket]}}

# Função de tratamento de interrupção
# Tentando evitar que a porta continue ocupada após o encerramento do servidor
def interrupt_handler(signum, frame):
    if serverSocket is not None:
        close_all_connections()
        serverSocket.close()
    os._exit(0)  # Termina o programa após enviar os dados correspondentes

def close_all_connections():
    for client in clients.keys():
        client.close()

    clients.clear()
    rooms.clear()

# Inicializa o socket globalmente (para que possa ser fechado no tratamento de interrupção)
signal.signal(signal.SIGINT, interrupt_handler)

def send_commands(connectionSocket):
    connectionSocket.sendall(f"{'=' * 50}\n".encode())
    connectionSocket.sendall("Checkout the commands below:\n".encode())
    connectionSocket.sendall("🔸 :help - List all available commands\n".encode())
    connectionSocket.sendall("🔸 :list - List all existing rooms\n".encode())
    connectionSocket.sendall("🔸 :users - List all users in the current room\n".encode())
    connectionSocket.sendall("🔸 :create <room_name> - Create a new room (joins automatically)\n".encode())
    connectionSocket.sendall("🔸 :join <room_name> - Join named room (if not already in a room)\n".encode())
    connectionSocket.sendall("🔸 :leave - Leaves current room (goes back to lobby)\n".encode())
    connectionSocket.sendall("🔸 :checkout <room_name> - switches from your current room to named room\n".encode())
    connectionSocket.sendall("🔸 :end - Ends connection with the server\n\n".encode())
    connectionSocket.sendall(f"{'=' * 50}\n".encode())

# Função de tratamento dos comando, retorna True se o comando for de encerramento
def handle_commands(connectionSocket, command, args):
    if command == ':help':
        send_commands(connectionSocket)
    
    elif command == ':checkout':
        if len(args) == 0:
            connectionSocket.sendall("Please provide a room name\n".encode())
            return False, False

        room_name = args[0]

        if room_name not in rooms:
            connectionSocket.sendall(f"Room {room_name} does not exist\n".encode())
            return False, False

        if clients[connectionSocket]['room'] != '':
            leave_room(connectionSocket)

        join_room(connectionSocket, room_name)

    elif command == ':create':
        if len(args) == 0:
            connectionSocket.sendall("Please provide a room name\n".encode())
            return False, False

        room_name = args[0]
        if room_name in rooms:
            connectionSocket.sendall(f"Room {room_name} already exists\n".encode())
            return False, False
        
        if len(rooms) == MAX_ROOMS:
            connectionSocket.sendall("Maximum number of rooms already reached\n".encode())
            return False, False
        
        create_room(connectionSocket, room_name)

        if clients[connectionSocket]['room'] != '':
            leave_room(connectionSocket) 

        join_room(connectionSocket, room_name)

    elif command == ':list':
        if rooms == {}:
            connectionSocket.sendall("No existing rooms\n".encode())

        for room in rooms.keys():
            connectionSocket.sendall(f"🚪 {room}\n".encode())

    elif command == ':join':
        if len(args) == 0:
            connectionSocket.sendall("Please provide a room name\n".encode())
            return False, False

        if clients[connectionSocket]['room'] != '':
            connectionSocket.sendall("You are already in a room\n".encode())
            return False, False

        room_name = args[0]

        if room_name not in rooms:
            connectionSocket.sendall(f"Room {room_name} does not exist\n".encode())
            return False, False

        join_room(connectionSocket, room_name)

    elif command == ':leave':
        if clients[connectionSocket]['room'] == '':
            connectionSocket.sendall("You are not in a room\n".encode())
            return False, False

        leave_room(connectionSocket)

        
    elif command == ':users':
        if clients[connectionSocket]['room'] == '':
            connectionSocket.sendall("You are not in a room\n".encode())
            return False, False

        room = rooms[clients[connectionSocket]['room']]

        for client in room:
            connectionSocket.sendall(f"👤 {clients[client]['username']}\n".encode())

    elif command == ':end':
        connectionSocket.sendall("Goodbye!".encode())

        if clients[connectionSocket]['room'] != '':
            leave_room(connectionSocket)

        clients.pop(connectionSocket)

        connectionSocket.close()
        return False, True
    
    elif command[0] != ':':
        return True, False

    else:
        connectionSocket.sendall("Invalid command\n".encode())

    return False, False # Não é mensagem, não é comando de encerramento

def create_room(connectionSocket, room_name):
    try:
        rooms[room_name] = []

        connectionSocket.sendall(f"Room {room_name} created\n".encode())
    
    except Exception as e:
        print(f"Error creating room: {e}")
        

def join_room(connectionSocket, room_name):
    rooms[room_name].append(connectionSocket)
    clients[connectionSocket]['room'] = room_name

    for client in rooms[room_name]:
        if client != connectionSocket:
            client.sendall(f"{clients[connectionSocket]['username']} has joined the room".encode())

    connectionSocket.sendall(f"Joined room {room_name}\n".encode())

def leave_room(connectionSocket):
    room_name = clients[connectionSocket]['room']
    room = rooms[room_name]
    username = clients[connectionSocket]['username']

    room.remove(connectionSocket)
    clients[connectionSocket]['room'] = ''

    for client in room:
        client.sendall(f"{username} has left the room".encode())    

    # Destroys room if it's empty
    if room == []:
        rooms.pop(room_name)
    

def handle_client(connectionSocket, addr):
    try:
        connectionSocket.sendall("Welcome to the server!\n".encode())

        send_commands(connectionSocket)

        # Only asks for username if the client is not already in the clients dictionary
        while connectionSocket not in clients.keys():
            user_taken = False
            connectionSocket.sendall("Please tell us your username: ".encode())
            username = connectionSocket.recv(1024).decode()
            
            if ":end" in username:
                connectionSocket.sendall("Goodbye!".encode())
                connectionSocket.close()
                return
            
            if username[0] == ':' or username == '':
                connectionSocket.sendall("Invalid username\n".encode())
                continue

            for client in clients.values():
                if client['username'] == username:
                    connectionSocket.sendall("Username already in use\n".encode())
                    user_taken = True
                    break

            if not user_taken:
                clients[connectionSocket] = {'username': username, 'room': ''}
                connectionSocket.sendall(f"Welcome {username}!\n".encode())

        while True:
            message = ''
            try:
                message = connectionSocket.recv(1024).decode()

                if not message:
                    continue

                command, *args = message.split()
                command = command.lower()

                message_flag, break_flag = handle_commands(connectionSocket, command, args)

                if message_flag:
                    if clients[connectionSocket]['room'] != '':
                        room = rooms[clients[connectionSocket]['room']]
                        username = clients[connectionSocket]['username']

                        for client in room:
                            if client != connectionSocket:
                                client.sendall(f"{username}: {message}".encode())

                if break_flag:
                    break
            except (IOError, IndexError):
                    connectionSocket.close()
                    break
        return
    
    except ConnectionRefusedError:
        print(f"Connection from {addr} has been refused!")

    except timeout:
        if clients[connectionSocket]['room'] != '':
            leave_room(connectionSocket)
        clients.pop(connectionSocket)
        print(f"Connection from {addr} has timed out!")

    finally:

        connectionSocket.close()

def main():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((SERVER_IP, SERVER_PORT))
    serverSocket.listen()

    print(f"Server is listening on port {SERVER_PORT}")

    while True:
        connectionSocket, addr = serverSocket.accept()
        threading.Thread(target=handle_client, args=(connectionSocket, addr)).start()

if __name__ == '__main__':
    main()


    