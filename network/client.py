import socket
import json
from threading import Thread
from communication.signals import Signals
from communication.global_data import PlayerData


class Client:

    def __init__(self, addr):
        self.addr = addr
        self.listen_tr = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(5)

    def connect(self):
        print(f'client: connecting to {self.addr}')
        try:
            self.sock.connect(self.addr)
            self.sock.settimeout(None)
            Signals().work.conn_attempt('ip', 'connected')
            self.sock.send(bytes(json.dumps({
                'msg': 'room_conn',
                'nickname': PlayerData().login,
                'room_slot': PlayerData().room_slot}), 'UTF-8'))
            self.listen_tr = Thread(target=self.handle_server, daemon=True)   # Thread???
            self.listen_tr.start()
            print(f'client: connected to {self.addr}')
        except Exception as e:
            Signals().work.conn_attempt('ip', 'failed')
            print(f'client error: {e}')

    def handle_server(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if data:
                    res = json.loads(data)
                    print(f'client received msg: {res}')

                    if res['msg'] == 'enemy_conn':
                        Signals().work.enemy_conn(f'{{"nickname":"{res["enemy_player"]["nickname"]}"}}')

                    if res['msg'] == 'enemy_choice':
                        Signals().work.enemy_choice(res['choice'])

                    if res['msg'] == 'room_ready':
                        Signals().work.room_ready()

                    if res['msg'] == 'start_game':
                        Signals().work.start_game(res['side'])

                    if res['msg'] == 'turn':
                        print('turn', res)
                        Signals().work.enemy_action(
                            f'{{"msg":"turn", "side":"{res["side"]}", "old_pos":{res["old_pos"]},'
                            f'"new_pos":{res["new_pos"]}, "kill_pos":{res["kill_pos"]}, "swap":{res["swap"]}}}')

                    if res['msg'] == 'transform':
                        print('transform', res)
                        Signals().work.enemy_action(
                            f'{{"msg":"transform","side":"{res["side"]}","kind":"{res["kind"]}",'
                            f'"grid_pos":{res["grid_pos"]}, "swap":{res["swap"]}}}')

            except Exception as e:
                print(f'client error: {e}')
                break

    def send_turn(self, side, old_pos, new_pos, kill_pos, swap):
        self.sock.send(bytes(json.dumps({
            "msg": "turn", "side": side,
            "old_pos": old_pos, "new_pos": new_pos, "kill_pos": kill_pos,
            "swap": swap}), 'UTF-8'))

    def send_transform(self, side, kind, grid_pos, swap):
        self.sock.send(bytes(json.dumps({
            "msg": "transform", "side": side,
            "kind": kind, "grid_pos": grid_pos,
            "swap": swap}), 'UTF-8'))
