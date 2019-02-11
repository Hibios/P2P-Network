from Cryptodome.PublicKey import DSA
import hashlib, binascii


def create_dsa_keys(code):
    key = DSA.generate(1024)
    encrypted_key = key.exportKey(
        passphrase=code,
        pkcs8=True,
        protection="PBKDF2WithHMAC-SHA1AndDES-EDE3-CBC"
    )
    with open("private_dsa_key.bin", "wb") as f:
        f.write(encrypted_key)
    with open("my_dsa_public.pem", "wb") as f:
        f.write(key.publickey().exportKey())
    return key.publickey().exportKey()


def password_encryption(password, salt):
    dk = hashlib.pbkdf2_hmac('sha256', b'password', b'salt', 100000)
    # Взврат зафированного пароля
    return binascii.hexlify(dk)


def hash(data):
    return hashlib.sha1(bytes(str(data), encoding='utf-8')).hexdigest()

#Хеш последней транзакции
def hash_transaction(transaction):
    hash_object = hashlib.sha256(bytes(transaction,'utf-8')).hexdigest()
    return hash_object

# Для тестирования ниже примеры вызовов (далее использовать по назначению)
# Вызов процедуры генерации ключей
# print(create_dsa_keys(input("Press random keys:\n")))
# Вызов шифрования пароля
# print(password_encryption(input("Enter password:\n"), input("Enter salt:\n")))
# Получение значения хэша от входных данных
# print(hash("spatiumblock"))
