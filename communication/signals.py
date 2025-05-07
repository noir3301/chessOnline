from PyQt6.QtCore import QObject, pyqtSignal
from utils import Singleton


class Signals(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.work = Worker()


class Worker(QObject):
    ip_conn_status = pyqtSignal(str)
    irc_network_status = pyqtSignal(str)
    sig_enemy_conn = pyqtSignal(str)
    sig_enemy_choice = pyqtSignal(str)
    sig_room_ready = pyqtSignal(str)
    sig_start_game = pyqtSignal(str)
    sig_enemy_action = pyqtSignal(str)

    sig_irc = pyqtSignal(str)

    def conn_attempt(self, conn_type, status):
        if conn_type == 'ip':
            if status == 'connected':
                self.ip_conn_status.emit('connected')
            elif status == 'failed':
                self.ip_conn_status.emit('failed')
        elif conn_type == 'irc':
            if status == 'connected':
                self.irc_network_status.emit('connected')
            elif status == 'failed':
                self.irc_network_status.emit('failed')

    def enemy_conn(self, enemy):
        self.sig_enemy_conn.emit(enemy)

    def enemy_choice(self, choice):
        self.sig_enemy_choice.emit(choice)

    def room_ready(self):
        self.sig_room_ready.emit('room_ready')

    def start_game(self, side):
        self.sig_start_game.emit(side)

    def irc(self, value):
        self.sig_irc.emit(value)

    def enemy_action(self, dict_val):
        self.sig_enemy_action.emit(str(dict_val))