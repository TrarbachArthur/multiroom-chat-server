from socket import *
from dotenv import load_dotenv
import os
import threading

# Função para lidar com informações recebidas pelo servidor
def server_stream(clientSocket):
    while True:
        try:
            message = clientSocket.recv(2048).decode()
            
            if not message:
                continue
            
            print(message)
        except:
            # Se houver erro na comunicação, quebra o loop
            break

    # Pode ser interessante checar se a conexão foi fechada pelo servidor

    # Encerra o cliente
    os._exit(0)


# Função para lidar com informações enviadas pelo cliente
def client_stream(clientSocket):
    while True:
        message = input()

        if not message:
            continue

        clientSocket.sendall(message.encode())

        # Se o cliente enviar o comando de encerramento, quebra o loop
        if message.lower() == ':end':
            break


def main():
    load_dotenv()
    
    SERVER_IP = os.getenv('SERVER_IP')
    SERVER_PORT = int(os.getenv('SERVER_PORT'))

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((SERVER_IP, SERVER_PORT))

    # Inicia a thread para lidar com as informações enviadas
    threading.Thread(target=server_stream, args=(clientSocket,)).start()
    # Define a thread principal para lidar com as informações recebidas
    client_stream(clientSocket)
    os._exit(0)

if __name__ == '__main__':
    main()