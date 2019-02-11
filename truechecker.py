""" Функции для проверки истинности различных данных, на данный момент последней транзакции"""

import db
from random import choice

def send_request(clients, host):
    """Функция получения списка new_clients из списка clients, 
    и выбора доступного избранника для проверки последней транзакции."""
    if not clients:
        return 'Нет клиентов!'
    else:
        new_clients = []
        for addr, port in clients:
            #Условие всегда исключает выбор клиента, который и отправил запрос.
            #Переменная host будет передаваться дальше, дабы потом на этот адрес отправить результаты.
            if addr != host:
                client = (addr, port)
                new_clients.append(client)
            else:
                pass

        random_client = choice(new_clients)
        print('Избранник для проверки: ' + str(random_client))