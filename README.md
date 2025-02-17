# multiroom-chat-server

Esse projeto é um servidor de salas de chat, desenvolvido em Python, e utilizando sockets TCP.
É possível criar salas, entrar e sair de salas existentes, enviar mensagens além de listar salas e usuários.
Por enquanto, a interface utilizada em 'client.py' é o terminal, mas existe espaço para desenvolvimento de uma interface web dedicada ao serviço de chat.

## Bibliotecas utilizadas:

- Socket: Implementação de sockets de comunicação.
- Threading: Utilização de threads.
- Python-dotenv: Leitura de arquivos .env, para configuração do servidor.
- os: Controle de processos e comandos do sistema operacional.

## Instalação

É necessário possuir Python 3.X . Então, basta seguir os seguintes passos:

```
git clone https://github.com/TrarbachArthur/multiroom-chat-server.git

cd multiroom-chat-server

pip install -r requirements.txt
```

Caso deseje alterar as configurações do servidor, é necessário alterar o arquivo .env, configurando as variáveis de ambiente.

```
SERVER_IP = IP do servidor (string).
SERVER_PORT = Porta do servidor (string). 
```

## Executando o servidor

Para executar o servidor, basta digitar o comando:

```
python server.py
```

Com o servidor rodando, é necessário iniciar os clientes, para utilizar o chat, para isso execute:

```
python client.py
```

## Utilizando a aplicação

Ao executar o cliente, o servidor enviará a lista de comando disponíveis, e será solicitado um nome de usuário, que não deve começar com ':'.
Digite o nome de usuário conforme solicitado e, após confirmação do servidor, poderá começar a utilizar os comandos disponíveis. O servidor deve se responsabilizar por impedir o uso incorreto dos comandos.

É importante ressaltar que o servidor exclui as salas que ficam vazias (sem nenhum usuário conectado).

## Testes de carga

Ao tentar realizar um teste de carga, o servidor apresentou um consumo desconsiderável de poder de processamento, além de 60 MB (0,1% de 12 GB * 5 usuários) de consumo de memória, para uma carga de 5 usuários conectados. . O aumento do número de usuários causou um crescimento linear no consumo de memória, devido à criação de threads “server.py” (mesmo que 0,1% aparente ser o mínimo que o método utilizado seja capaz de exibir), portanto, é **seguro** dizer que, em um cenário pessimista, um servidor que atenda um máximo de 50 usuários terá um consumo de memória de aproximadamente 600 MB.

## Funcionalidades

✅ - Servidor multithread para atendimente de multíplos clientes simultaneamente.

✅ - Sistema multisala, permitindo que usuários troquem mensagens apenas com usuários presentes na mesma sala.

✅ - Comandos de gerenciamento de salas e usuários (criar, listar, entrar, sair, ...).

✅ - Sistema de usuários (sem autenticação).

🕐 - Criação de diferentes sockets para cada sala existente, descentralizando a recepção das mensagens e comandos.

🕐 - Autenticação de usuários.

🕐 - Log de mensagens, permitindo recuperar um histórico das mensagens enviadas.

🕐 - Criação de salas privadas (protegidas por senha)

🕐 - Cargo administrador, para gerenciamento do sistema no geral (controle de diversas salas)

🕐 - Interface web