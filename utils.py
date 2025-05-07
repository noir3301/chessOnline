import socket
import requests
import random
import string
import sys, linecache
import logging
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.handler = logging.FileHandler(f"py.log", mode='w')
        self.logger.addHandler(self.handler)

    def write_info(self, info_dict):
        for key, value in info_dict.items():
            self.logger.info(f"{key}: {value}")


class Validation:
    def __init__(self, *args):
        pass

    @classmethod
    def validate(cls, validation_type, validation_value):
        match validation_type:
            case 'login':
                return cls.login(validation_value)
            case 'email':
                return cls.email(validation_value)
            case 'password':
                return cls.password(validation_value)
            case 'ip_port':
                return cls.ip_port(validation_value)
            case _:
                return False

    @staticmethod
    def login(login):
        if len(login) < 3 or len(login) > 15:
            return False
        return True

    @staticmethod
    def email(email):
        return True

    @staticmethod
    def password(password):
        return True

    @staticmethod
    def ip_port(ip_port):
        ip_port_s = ip_port.split(':')
        if len(ip_port_s) != 2:
            return False
        else:
            ip = ip_port_s[0]
            port = ip_port_s[1]
        if not str(port).isdigit():
            return False
        if ip == 'localhost':
            return True
        try:
            socket.inet_aton(ip)
            return True
        except:
            return False


def add_widgets(layout: QVBoxLayout | QHBoxLayout, widgets: tuple):
    [layout.addWidget(widget) for widget in widgets]

def get_public_ip():
    try:
        r = requests.get(r'http://jsonip.com')
        ip = r.json()['ip']
        return ip
    except:
        return False

def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return False

def random_word(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
