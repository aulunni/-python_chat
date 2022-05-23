import socket
from threading import Thread
import json

# подключение к серверу
HOST = '127.0.0.1'
PORT = 8888
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


# функция для получений сообщений от сервера
def recv_from_server():
    while True:
        data = client_socket.recv(4096)
        msg = json.loads(data.decode('utf-8'))
        # сообщение в общем чате
        if msg['action'] == 'new_message':
            print('[{}]: {}'.format(msg['from'], msg['text']))
        # новый пользователь на сервере
        elif msg['action'] == 'new_user':
            print('Приветствуем ' + msg['user'])
        # пользователь из списка ушел с сервера
        elif msg['action'] == 'user_left':
            print(msg['user'] + ' Бросил(a) нас!')
        # личное сообщение пользователю
        elif msg['action'] == 'new_whisper':
            print('[{} шепчет Вам]: {}'.format(msg['from'], msg['text']))
        # вывод непредвиденных ошибок
        elif msg['action'] == 'error':
            print('Ошибка: ' + msg['text'])


# функция для отправки сообщений серверу
def send_to_server(name):
    while True:
        text = input()
        if text[0] == '\\':
            if text[1] == 'w':
                args = text.split(' ')
                args.remove(args[0])
                send_to = args[0]
                args.remove(args[0])
                # если в отправленном есть "w", то отправляем лишь указанному пользователю
                request = {'action': 'new_whisper',
                           'to': send_to,
                           'text': ' '.join(args)}
                msg = json.dumps(request).encode('utf-8')
                client_socket.send(msg)
        # в остальных случаях отправляется общее сообщение в чат
        else:
            request = {'action': 'new_message',
                       'text': text}
            msg = json.dumps(request).encode('utf-8')
            client_socket.send(msg)


# регистрация пользователя
def registration():
    while True:
        name = input('Введите имя: ')
        # нельзя взять пустое имя
        if ' ' in name or name == '':
            print('Не корректное имя!')
            continue
        request = {'action': 'registration',
                   'name': name}
        msg = json.dumps(request).encode('utf-8')
        client_socket.send(msg)
        response = client_socket.recv(4096)
        result = json.loads(response.decode('utf-8'))
        if result['result'] == 'successful':
            print(result['text'])
            for user in result['users']:
                print('\t{0}'.format(user))
            break
        # нельзя взять имя, занятое другим пользователем
        else:
            print('Имя уже занято!')
    return name


if __name__ == '__main__':
    name = registration()
    send_thread = Thread(target = send_to_server, args = (name, ))
    recv_thread = Thread(target = recv_from_server, args = ())
    send_thread.start()
    recv_thread.start()
    send_thread.join()
    recv_thread.join()
