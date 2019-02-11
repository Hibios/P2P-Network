"""Модуль использует netsh для отключения брандмауэра"""

import subprocess
import os
import portforwardlib
import time

protocol = 'UDP'

try:
    def offer():
        print('Отключение advfirewall:')
        subprocess.check_call('netsh.exe advfirewall set publicprofile state off')
except:
    print('Ошибка отключения брандмауэра.')

try:
    def redirectport(ip):
        result = None
        while result == None:
            try:
                print('Начал перенаправление порта.')
                result = portforwardlib.forwardPort(9090, 9090, None, ip, False, protocol, 0, 'SpatiumBlockNetwork({})'.format(protocol), True)
            except:
                print('Не удалось перенаправить порт.')
            time.sleep(0.3)
except:
    print('Ошибка при перенаправлении портов.')

try:
    def close_port(ip):
        result = None
        while result == None:
            try:
                result = portforwardlib.forwardPort(9090, 9090, None, ip, False, protocol, 1,
                                                    'SpatiumBlockNetwor({})'.format(protocol), False)
                print(result)
            except Exception as e:
                print(e)
                pass
            time.sleep(0.3)
except:
    print('Ошибка при закрытии порта.')