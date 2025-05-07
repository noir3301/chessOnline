import socket
from threading import Thread
import json
import time
import random


class Server:
    conns = []

    def __init__(self, addr, max_players):
        self.threads_pool = []
        self.max_conns_flag = False
        self.exception = None
        self.players = []
        self.addr = addr
        self.max_players = max_players
        self.sides = ['white', 'black']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(addr)
            self.sock.listen(self.max_players)
        except Exception as e:
            self.exception = e
            print(f'server error: {e}')


    def listen(self, serv_stop_event):
        print(f'server: running on {self.addr}')
        Thread(target=self.prevent_blocking, daemon=True, args=(serv_stop_event,)).start()
        while not serv_stop_event.is_set():
            if len(self.players) < self.max_players:
                conn, addr = self.sock.accept()
                self.conns.append(conn)
                print(f'server: new connection {addr}')
                self.players.append({'addr': addr, 'nickname': None, 'room_slot': None, 'is_ready': False, 'side': None})
                self.threads_pool.append(Thread(target=self.handle_client, daemon=True, args=(conn,)))
                self.threads_pool[-1].start()
            else:
                self.max_conns_flag = True # terminate prevent blocking thread if 2 players are connected
                while self.threads_pool[0].is_alive() or self.threads_pool[1].is_alive():   ### TEMP while
                    time.sleep(1)
        print('server: shutdown')

    def prevent_blocking(self, serv_stop_event):
        while not serv_stop_event.is_set():
            time.sleep(0.5)
            if self.max_conns_flag:
                print('server: max connections has been reached')
                return
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self.addr)
        self.sock.close()

    def handle_client(self, conn):
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    print("Disconnect")
                    break

                data = data.decode('utf-8').replace('}{', '}|{').split('|')
                for d in data:
                    res = json.loads(d)
                    print(f'server received msg: {res} from {conn.getpeername()}')

                    if res['msg'] == 'room_conn':
                        index = [i for i, player in enumerate(self.players) if player['addr'] == conn.getpeername()][0]
                        self.players[index]['nickname'] = res['nickname']
                        self.players[index]['room_slot'] = res['room_slot']
                        if len(self.players) == 2 and all([self.players[0]['nickname'], self.players[1]['nickname']]):
                            for c in self.conns:
                                enemy_player = \
                                    [player for player in self.players if player['addr'] != c.getpeername()][0]
                                c.send(bytes(json.dumps({'msg': 'enemy_conn', 'enemy_player': enemy_player}),
                                             'UTF-8'))

                    if res['msg'] == 'enemy_choice':
                        index = [i for i, player in enumerate(self.players) if player['addr'] == conn.getpeername()][0]
                        self.players[index]['choice'] = res['choice']
                        for c in self.conns:
                            if c != conn:
                                c.send(bytes(json.dumps({'msg': 'enemy_choice', 'choice': res['choice']}), 'UTF-8'))

                    if res['msg'] == 'room_ready':
                        index = [i for i, player in enumerate(self.players) if player['addr'] == conn.getpeername()][0]
                        self.players[index]['is_ready'] = True
                        for c in self.conns:
                            if c != conn:
                                c.send(bytes(json.dumps({'msg': 'room_ready'}), 'UTF-8'))
                        if self.players[0]['is_ready'] and self.players[1]['is_ready']:
                            print('ALL READY')
                            sides = [self.players[0]['side'], self.players[1]['side']]
                            if sides[0] == sides[1]:
                                rand = random.randint(0, 1)
                                self.players[0]['side'] = self.sides[rand]
                                self.players[1]['side'] = self.sides[abs(rand - 1)]
                            elif ('white' in sides or 'black' in sides) and 'random' in sides:
                                rand_ind = sides.index('random')
                                ch_ind = abs(rand_ind - 1)
                                self.players[rand_ind]['side'] = self.sides[abs(self.sides.index(sides[ch_ind]) - 1)]
                            for c in self.conns:
                                player = [p for p in self.players if p['addr'] == c.getpeername()][0]
                                c.send(bytes(json.dumps({'msg': 'start_game', 'side': player['side']}), 'UTF-8'))

                    if res['msg'] == "turn":
                        print('turn')
                        for c in self.conns:
                                c.send(bytes(json.dumps({
                                    'msg': 'turn', 'side': res['side'],
                                    'old_pos': res['old_pos'], 'new_pos': res['new_pos'], 'kill_pos': res['kill_pos'],
                                    'swap': res['swap']}), 'UTF-8'))

                    if res['msg'] == "transform":
                        print('transform')
                        for c in self.conns:
                            c.send(bytes(json.dumps({
                                'msg': 'transform', 'side': res['side'],
                                'kind': res['kind'], 'grid_pos': res['grid_pos'],
                                'swap': res['swap']}), 'UTF-8'))

            except Exception as e:
                print(f'server error: {e}')
                break
