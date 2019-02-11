import sqlite3
import datetime
import time
connection = object
def init():
    global connection
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE if not exists addresses
                      (ID INTEGER PRIMARY KEY, address STRING, port INTEGER)
                    """)
    cur.execute("""CREATE TABLE if not exists client
                      (wallet varchar, public_key varchar, private_key varchar)
                    """)
    cur.execute("""CREATE TABLE if not exists history
                      (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, from_id, message text,
                       to_id text, date int)
                    """)
    cur.execute("""CREATE TABLE if not exists users
                      (ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, public_key VARCHAR, 
                      balance VARCHAR NOT NULL)
                    """)
    connection = conn
#здесь проверка новой транзакции на наличие в базе (временно)
def check_event(data):
    string = data.split(":")
    cursor = connection.cursor()
    sql = "SELECT * FROM history WHERE id=?,from_id=?,message=?,date=?,to_id=?"
    cursor.execute(sql,[string[1],string[2],string[3],string[4],string[5]])
    result = cursor.fetchone()
    if result != None:
        print("Попытка взлома!")
    else:
        string = (str())
        add_event(string)
# добавляем новое событие в базу
def add_event(string):
    data = string.split(":")
    cursor = connection.cursor()
    sql = """INSERT INTO history(from_id,message,to_id,date) VALUES(?,?,?,?)"""
    cursor.execute(sql, [data[0],data[1],data[2],str(int(time.time()))])
    connection.commit()
#получить последнюю транзакцию из истроии в базе
def get_last_transaction():
    cursor = connection.cursor()
    sql = "SELECT * FROM history ORDER BY ID DESC LIMIT 1"
    cursor.execute(sql)
    last_tx = cursor.fetchone()
    return last_tx
#Получаем список базовых нод
def get_nodes():
    cursor = connection.cursor()
    sql = "SELECT address, port FROM addresses"
    cursor.execute(sql)
    nodes = cursor.fetchall()
    return nodes
#внесение данных пользователя в базу (используется единожды)
def create_user(public_key):
    cursor = connection.cursor()
    sql= """INSERT INTO users(public_key) VALUES(?,?)"""
    cursor.execute(sql, [public_key,private_key])
    connection.commit()
# возрващает публичный ключ пользователя
def get_key(wallet):
    cursor = connection.cursor()
    sql = "SELECT public_key FROM users WHERE public_key=?"
    cursor.execute(sql,[wallet])
    data = cursor.fetchone()
    if data == None:
        sql = "INSERT INTO users(public_key,balance) VALUES (?,?)"
        cursor.execute(sql,[wallet,0])
        connection.commit()
    return data
# возрващает список транзакций, где from_id=wallet. wallet=public key
def get_transactions(wallet):
    cursor = connection.cursor()
    sql = """SELECT * FROM history WHERE from_id=?"""
    cursor.execute(sql, [str(wallet)])
    result = cursor.fetchall()
    return result