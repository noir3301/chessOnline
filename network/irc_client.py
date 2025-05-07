import socket
import ssl
from threading import Thread
from communication.signals import Signals


class IRC:
    HOST = 'irc.oftc.net'
    #HOST = 'irc.dal.net'
    REALNAME = 'pyclient'
    CHANNEL = "FBfkseGJESRCskafwj4r238f"
    SSOCK = None

    def __init__(self, nickname, stop_event):
        self.nickname = nickname
        self.stop_event = stop_event
        self.context = ssl.create_default_context()
        Signals().work.sig_irc.connect(self.irc_signals)

    def connect(self):
        ident = self.nickname
        try:
            with socket.create_connection((self.HOST, 6697)) as sock:
                with self.context.wrap_socket(sock, server_hostname=self.HOST) as ssock:
                    print(ssock.version())
                    IRC.SSOCK = ssock
                    ssock.send(("NICK %s\r\n" % self.nickname).encode())
                    ssock.send(("USER %s %s %s :%s\r\n" % (ident, self.HOST, self.nickname, self.REALNAME)).encode())
                    ssock.send(("JOIN #" + self.CHANNEL + " \r\n").encode())
                    ssock.send(("PRIVMSG #" + self.CHANNEL + " :ONLINE\r\n").encode())
                    ssock.send(("PRIVMSG #" + self.CHANNEL + " :ONLINE555\r\n").encode())
                    while not self.stop_event.is_set():
                        rec = ssock.recv(1024)
                        temp = rec.decode().split('\r\n')[:-1]
                        for i, line in enumerate(temp):
                            print(line)
                            if 'Erroneous Nickname' in line or 'Nickname is already in use' in line:
                                Signals().work.conn_attempt('irc', 'failed')
                                print('irc client: connection failed')
                                return
                            if ('JOIN :#'+self.CHANNEL) in line:
                                Signals().work.conn_attempt('irc', 'connected')
                                print('irc client: connected to channel')
                                self.handle_server()

                    print('irc client: shutdown')
        except Exception as e:
            print('irc error:', e)
        print('irc client: shutdown')

    def handle_server(self):
        while not self.stop_event.is_set():
            rec = IRC.SSOCK.recv(1024)
            temp = rec.decode().split('\r\n')[:-1]
            for line in temp:
                print(line)

    def irc_signals(self, value):
        print(value)
        conn_type, room_name = value.split('|')
        print(conn_type)
        if conn_type == 'create':
            IRC.SSOCK.send(("PRIVMSG #" + self.CHANNEL + " :CREATE\r\n").encode())
        elif conn_type == 'join':
            IRC.SSOCK.send(("PRIVMSG #" + self.CHANNEL + " :JOIN\r\n").encode())

