from scenes.room.ui import UI, ChoiceBox, ReadyButton
from communication.global_data import PlayerData, NetworkData
from communication.signals import Signals
import json


class Agent:
    def __init__(self):
        Signals().work.sig_enemy_conn.connect(self.enemy_connect)
        Signals().work.sig_enemy_choice.connect(self.receive_choice)
        Signals().work.sig_room_ready.connect(self.set_ready)
        Signals().work.sig_start_game.connect(self.game_start)
        ChoiceBox.BOUND_FUNC = self.send_choice
        ReadyButton.BOUND_FUNC = self.send_ready
        self.ui = UI()

    def self_connect(self):
        my_slot_ins = self.ui.main_box.slots_ins[PlayerData().room_slot]
        my_slot_ins.player_box.login_label.set_login(PlayerData().login)
        my_slot_ins.player_box.setHidden(False)

    def enemy_connect(self, enemy):
        print(f'enemy connect signal: {enemy}')
        enemy_login = json.loads(enemy)['nickname']
        PlayerData().enemy_login = enemy_login
        my_slot_ins = self.ui.main_box.slots_ins[PlayerData().room_slot]
        enemy_slot_ins = self.ui.main_box.slots_ins[abs(PlayerData().room_slot - 1)]
        enemy_slot_ins.player_box.login_label.set_login(enemy_login)
        enemy_slot_ins.player_box.setHidden(False)
        my_slot_ins.player_box.choice_box.enable_choices()

    @staticmethod
    def send_choice(choice):
        NetworkData().client.sock.send(bytes(json.dumps({
                'msg': 'enemy_choice',
                'nickname': PlayerData().login,
                'room_slot': PlayerData().room_slot,
                'choice': choice}), 'UTF-8'))

    def receive_choice(self, kind):
        enemy_choice_box = self.ui.main_box.slots_ins[abs(PlayerData().room_slot - 1)].player_box.choice_box
        [choice.clear_border() for choice in enemy_choice_box.choices.values()]
        enemy_choice_box.cur_choice = enemy_choice_box.choices[kind]
        enemy_choice_box.choices[kind].set_border()

    @staticmethod
    def send_ready():
        NetworkData().client.sock.send(bytes(json.dumps({
            'msg': 'room_ready',
            'nickname': PlayerData().login,
            'room_slot': PlayerData().room_slot}), 'UTF-8'))

    def set_ready(self):
        enemy_ready_btn = self.ui.main_box.slots_ins[abs(PlayerData().room_slot - 1)].player_box.ready_btn
        enemy_ready_btn.clicked_flag = True
        enemy_ready_btn.set_ready_style()

    def game_start(self, side):
        PlayerData().side = side
        if side == 'white':
            PlayerData().turn = True
            PlayerData().enemy_side = 'black'
        else:
            PlayerData().enemy_side = 'white'
        self.ui.window().set_game_scene()
        print('YOUR SIDE:', side)
