"""
Главный файл, используемый для запуска клиента в сеть.
"""
# Импорт скриптов
# service_functions - все необходимые функции для работы программы
import service_functions as func
import portforwardlib as frw
import firewalloff
from requests import get
import db

# Импорт модулей
import json
import os
import sys
import socket
import threading
import pickle
import time


try:
    print('Получение внешнего IP...')
    real_host = get('https://api.ipify.org').text
except:
    print('Внешний адрес не получен.')

print('Внешний IP: {}'.format(real_host))

# берём адрес внутреннего хоста
host = frw.get_my_ip()
if str(real_host) == str(host):
    print("Проброс портов не нужен.")
else:
    try:
        firewalloff.redirectport(host)
    except TimeoutError:
        firewalloff.offer()

clients = []
nodes = "node.json"

# список "стартовых" нод.
base_node = []

# инициализация сокет-объекта
# s1 - входящий сокет
s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s1.bind((host, 9090))
s1.setblocking(0)
# s2 - исходящий сокет
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2.bind((host, 0))
s2.setblocking(0)

# статус клиента: 0-запуск клиента, 1-работа в оффлайн режиме, 2-подключен к сети
client_status = 0
exit = 0

#Пока переменная ложна продолжается прслушивание сообщений
shutdown = False

"""
----------------------------------------------------------------------------------------------------
Ниже идет главный код, все backend функции писать выше
Все frontend функции писать ниже
----------------------------------------------------------------------------------------------------
"""

func.init(s1, s2, host, shutdown, nodes, base_node, real_host)
public_key = db.get_key(func.get_config("wallet", host))
exitt = 0
while exitt == 0:
    try:
        print("Аккаунт: %s\n----------" % public_key)
        print("Статус клиента: %s" % str(func.get_status()))
        print("Локальный IP: {0}".format(host))
        try:
            # Попытка вывести внешний ip если он найден.
            print("Внешний IP: {0}".format(real_host))
        except NameError:
            pass

        message = "1.Отправить сообщение\n" + \
                  "2.Посмотреть последнюю транзакцию\n" + \
                  "3.Посмотреть историю транзакций\n" + \
                  "4.Посмотреть список клиентов\n" + \
                  "5.Проверить последнюю транзакцию\n" + \
                  "6.Проверить подключение к сети\n"

        choose = input(message + ': ')

        if choose == "1":
            text = input("Введите сообщение: ")
            to = input("Получатель: ")
            if any(to in addr for addr, prt in clients):
                string = (str(public_key[0]) + ":" + str(core.hash(text)) + ":" + str(to))
                try:
                    mess = 'message::' + text
                    s1.sendto(ttb(mess), (to, 9090))
                    db.add_event(string)
                    print("Сообщение отправлено по адресу: {}, {}".format(to, 9090))
                except:
                    print("Ошибка при отправке сообщения!")
            else:
                print('Клиент с IP - {} не подключен к сети.'.format(to))

        elif choose == "2":
            last_tx = db.get_last_transaction()
            if last_tx is not None:
                print(
                    "Последняя транзакция:\nid {0}\nОт кого: {1}\nсообщение: {2}\nКому: {3}\nДата: {4}\n----------------\n".format(
                        last_tx[0], last_tx[1], last_tx[2], last_tx[3], date(last_tx[4])))
            else:
                print("Транзакций не найдено!")
        elif choose == "3":
            wallet = input("Введите свой адрес: ")
            result = db.get_transactions(wallet)
            for i in result:
                print(
                    "id {0}\nОт кого: {1}\nСообщение: {2}\nКому: {3}\nДата: {4}\n----------------\n".format(
                        i[0], i[1], i[2], i[3], date(i[4])))
        elif choose == "4":
            for i in clients:
                print("\n-------\n{0}".format(i))

        # |||Проверка истинности последней транзакции начинается здесь.|||
        elif choose == "5":
            last_tx = db.get_last_transaction()
            if last_tx is not None:
                data = str(last_tx[0]) + str(last_tx[1]) + str(last_tx[2]) + str(last_tx[3]) + str(date(last_tx[4]))
                print("Хеш последней транзакции: " + core.hash_transaction(data))
                truechecker.send_request(clients, host)
            else:
                print("Транзакций не найдено!")

        # Проверка подключения.
        # Достаточно ли в сети к которой мы подключены клиентов?
        elif choose == "6":
            global room
            room = 0
            for node in clients:
                # Отправляем запрос на проверку подключения к сети каждому в списке клиентов.
                s1.sendto(bytes("check_connect::", encoding='utf-8'), node)

        elif choose == "clients":
            print(clients)


    except KeyboardInterrupt:
        print("Вы действительно хотите выйти? Y/n")
        type = input()
        if type.lower() == "n":
            pass
        else:
            shutdown = True
            print("1")
            for i in clients:
                print(i)
                try:
                    print('Сообщено клиенту: {0} {1}'.format(i[0], 9090))
                    s1.sendto(bytes("quit::", encoding='utf-8'), (i[0], 9090))
                except:
                    pass
            s1.close()
            s2.close()
            print(firewalloff.close_port(host))
            print("2")
            exit = 1
            sys.exit(0)

