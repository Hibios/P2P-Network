""" 
----------------------------
Функции для файла client.py 
----------------------------
"""
# Импорт нужных скриптов и библиотек
import db
import threading

def strto(string):
    """Коневртация в байты"""
    return bytes(string, encoding='utf-8')

def byteto(bytes):
    """Коневртация в строку"""
    return str(bytes.encode("utf-8"))

def date(timestamp):
    """
    Конвертация unix timestamp в формат обычной даты
    """
    import datetime
    return (
        datetime.datetime.fromtimestamp(
            int(timestamp)
        ).strftime('%Y-%m-%d %H:%M:%S')
    )

def preparation(node_list, base_node, real_host):
    """
    Подготовка переменных с клиентскими адресами
    """
    for node in node_list:
        base_node.append(node)
    # Удаляет из базовых узлов, свой ip если найдёт его
    for node in base_node:
        for addr in node:
            if addr == real_host:
                base_node.remove(node)

def get_config(data, host):
    """ Создание названия аккаунта """
    if data == "wallet":
        return str("test" + str(host))

def get_status():
    """Получение статуса клиента"""
    if client_status == 0:
        return "Оффлайн"
    elif client_status == 1:
        return "Поиск пиров..."
    elif client_status == 2:
        return "Подключен к сети"


def init(s1, s2, host, shutdown, nodes, base_node, real_host):
    """
    Инициализирующая функция. Cюда добавлять процедуры, которые нужно выполнить на старте программы.
    """
    global client_status
    #try:
    db.init()
    node_list = db.get_nodes()
    preparation(node_list, base_node, real_host)
    print("База данных загружена")
    #except:
        #print("Ошибка при загрузке баы данных")
    client_status = 1
    try:
        # запуск основных потоков
        threading.Thread(target=receving, args=(s1,host,shutdown,)).start()
        threading.Thread(target=receving, args=(s2,host,shutdown,)).start()
        init_connection(s2, nodes, base_node, host)
    except Exception as e:
        print("Error.")
        print(e)
        pass

def receving(sock, host, shutdown):
    """ 
    Поток для принятия входящих сообщений 
    """

    while shutdown == False:
        try:
            global clients
            while True:
                # ниже обработка входящих сообщений
                all_data = bytearray()
                while len(all_data) == 0:
                    try:
                        data, addr = sock.recvfrom(2048)
                        """
                        Фикс на статус, если данные удаётся получить, 
                        следовательно клиенты подключились друг к другу.
                        """
                        print('\nСвязь установлена!')
                        global client_status
                        client_status = 2

                        if addr[0] != host:
                            # Клиент на проверку
                            check_user(addr)
                        if not data:
                            break
                        all_data = all_data + data
                    except:
                        pass
                if addr[0] != host:
                    print("Запрос от " + str(addr) + " " + str(data.decode("utf-8")))
                    data = data.decode("utf-8")
                    data = data.split("::")
                    threading.Thread(target=sort_data, args=(data, addr, sock,)).start()
        except KeyboardInterrupt:
            shutdown = True
        except:
            pass
    exit = 1

def check_user(ip):
    """
    Функция проверяет клиентов по правилам и добавляет его в список клиентов
    """
    print('Проверка клиентов...')
    global clients
    check = 0
    for i in clients:
        if i[0] == ip[0]:
            check = 1
        elif i[0] == host:
            check = 1
    if ip[0] == host:
        check = 1
    try:
        # Наше спасительное условие от нежелательных реальных ip
        # Исключение здесь на тот случай,
        # если первое исключение не даст нам реальный ip, и real_host не существует
        if ip[0] == real_host:
            check = 1
    except NameError:
        pass

    if check == 0:
        clients.append(ip)
    else:
        pass

def sort_data(data, addr, sock):
    """
    Здесь обработка входящего сообщения
    """
    global clients
    if data[0] == "new_event":
        db.check_event(data)
    elif data[0] == "check_db":
        sock.sendto(core.hash(db.get_last_transaction()), addr)
    elif data[0] == "get_peers":
        if len(clients) == 0:
            sock.sendto("peers::None", addr)
        else:
            table = "peers::"
            for i in clients:
                table = str(table + str(i) + ",,")
            sock.sendto(ttb(table), addr)
    elif data[0] == "peers":
        if data[1] == "None":
            print("Новых клиентов не найдено!")
            # init_connection(sock)
        else:
            list = data[1][:-2]
            new_list = list.split(",,")
            for i in new_list:
                if i not in clients:
                    check_user(eval(i))
        next_connection(sock)

    elif data[0] == "ping":
        sock.sendto(bytes("pong::", encoding='utf-8'), addr)

    # Если придёт данный запрос, сообщить клиенту: Я здесь!
    elif data[0] == "check_connect":
        sock.sendto(bytes("here::", encoding='utf-8'), addr)

    elif data[0] == "here":
        global room
        room += 1
        print("Ответ от клиента {}: нахожусь в сети.".format(addr))

    elif data[0] == "message":
        print("Текстовое сообщение от клиента {}: {}".format(addr, byte_to_string(data[1])[2:-1]))

    elif data[0] == "pong":
        sock.sendto(ttb("get_peers::"), addr)
        if addr not in clients:
            print('Добавлен', addr)
            clients.append(addr)
    elif data[0] == "pingg":
        sock.sendto(ttb("pongg::"), addr)
    elif data[0] == "quit":
        # Если реальный хост присутствуют в клиентах
        for address, poort in clients:
            if addr[0] == address:
                a = (address, poort)
                clients.remove(a)
                print("Отключился клиент {0}".format(a))
        if not clients:
            global client_status
            client_status = 1

# Процедура первого подключения при старте (нужно доделать)
def init_connection(sock, nodes, base_node, host):
    """
    Процедура первого подключения при старте
    """
    try:
        f = open(nodes)
        ff = f.readlines()
        # ff=список с нодами
        for i in ff:
            try:
                sock.sendto(bytes("ping::", encoding='utf-8'), i)
                break
            except Exception:
                pass
    except FileNotFoundError:
        for i in base_node:
            # проходим стартовые ноды, если нету клиентов
            if i[0] != host and i[0] != 'localhost' and i[0] != '':
                text = bytes("ping::", encoding='utf-8')
                try:
                    sock.sendto(text, i)
                except:
                    print('Не удалось отправить ping.')