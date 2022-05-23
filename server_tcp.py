import socket
import select
import json

# подключение пользователь к серверу
CONNECTION_LIST = []
USERS = {}
RECV_BUFFER = 4096
PORT = 8888
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(10)
CONNECTION_LIST.append(server_socket)


# функция, которая выводит отправленные клиентом сообщения в терминал сервера
def main():
    while True:
        rList, wList, error_sockets = select.select(CONNECTION_LIST, [], [])
        for sock in rList:
            if sock == server_socket:
                # подключение клиента
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print("Client (%s, %s) connected" % addr)
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    msg = json.loads(data.decode('utf-8'))
                    if msg['action'] == 'registration':
                        registration(sock, msg)
                    elif msg['action'] == 'new_message':
                        new_message(sock, msg)
                    elif msg['action'] == 'new_whisper':
                        new_whisper(sock, msg)
                except Exception as e:
                    # print(e)
                    # отключение клиента от сервера
                    print("client disconnect")
                    user_left(sock)
                    CONNECTION_LIST.remove(sock)
                    for user in USERS:
                        if USERS[user] == sock:
                            del USERS[user]
                            break
                    sock.close()


# регистрация пользователя
def registration(sock, msg):
    if msg['name'] not in USERS.keys():
        USERS.update({msg['name']: sock})
        new_user(sock, msg)
        # ответ после успешной регистрации
        response = {'result': 'successful',
                    'text': 'Првиетствуем в чате! Для личных сообщений используйте "\w"! Сейчас в сети: ',
                    'users': list(USERS.keys())}
        msg = json.dumps(response).encode('utf-8')
        sock.send(msg)
    # ответ при неудачной регистрации
    else:
        response = {'result': 'error'}
        msg = json.dumps(response).encode('utf-8')
        sock.send(msg)


# появление нового пользователя
def new_user(sock, msg):
    response = {'action': 'new_user',
                'user': msg['name']}
    msg = json.dumps(response).encode('utf-8')
    for user in USERS:
        if USERS[user] == sock:
            continue
        else:
            USERS[user].send(msg)


# отключение пользователя
def user_left(sock):
    for user in USERS:
        if USERS[user] == sock:
            name = user
    response = {'action': 'user_left',
                'user': name}
    msg = json.dumps(response).encode('utf-8')
    for user in USERS:
        if USERS[user] == sock:
            continue
        else:
            USERS[user].send(msg)


# отправка сообщения в общий чат
def new_message(sock, msg):
    for user in USERS:
        if USERS[user] == sock:
            name = user
    response = {'action': 'new_message',
                'text': msg['text'],
                'from': name}
    msg = json.dumps(response).encode('utf-8')
    for user in USERS:
        if USERS[user] == sock:
            continue
        else:
            USERS[user].send(msg)


# новое личное сообщение
def new_whisper(sock, msg):
    for user in USERS:
        if USERS[user] == sock:
            name = user
    if msg['to'] in USERS.keys():
        to_ = msg['to']
        response = {'action': 'new_whisper',
                    'text': msg['text'],
                    'from': name}
        msg = json.dumps(response).encode('utf-8')
        USERS[to_].send(msg)
    # обработка ошибок при неправильно указанном пользователе
    else:
        response = {'action': 'error',
                    'text': 'Пользователь ' + msg['to'] + ' не найден!'}
        msg = json.dumps(response).encode('utf-8')
        sock.send(msg)


if __name__ == '__main__':
    main()
