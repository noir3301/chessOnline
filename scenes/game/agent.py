from requests.utils import default_user_agent

from scenes.game.ui import UI, Queen, Rook, Bishop, Horse, GameEndText
from scenes.game.core.figure import Figure, Mark
from communication.global_data import PlayerData, ConfigData
from communication.signals import Signals
from utils import print_exception
import json


class Agent:
    def __init__(self):
        self.ui = UI()
        Signals().work.sig_enemy_action.connect(self.rec_enemy_action)


    def rec_enemy_action(self, dict_val):
        try:
            res = json.loads(dict_val)
            if res['side'] != PlayerData().side:
                if res['msg'] == 'turn':
                    res['kill_pos'] = (abs(7 - res['kill_pos'][0]), abs(7 - res['kill_pos'][1]))
                    res['old_pos'] = (abs(7 - res['old_pos'][0]), abs(7 - res['old_pos'][1]))  # convert pos
                    res['new_pos'] = (abs(7 - res['new_pos'][0]), abs(7 - res['new_pos'][1]))  # convert pos
                    self.change_pos(res['old_pos'], res['new_pos'], res['kill_pos'])
                if res['msg'] == 'transform':
                    res['grid_pos'] = (abs(7 - res['grid_pos'][0]), abs(7 - res['grid_pos'][1]))  # convert pos
                    self.transform_fig(res['kind'], res['grid_pos'])
                if res['swap']:
                    PlayerData().turn = True
                self.check_handler(PlayerData().enemy_king, PlayerData().king, PlayerData().side)
            else:
                self.check_handler(PlayerData().king, PlayerData().enemy_king, PlayerData().enemy_side)

            if res['msg'] == 'turn':
                self.mark_last_move(res)
        except:
            print_exception()

    def change_pos(self, old_pos, new_pos, kill_pos):
        try:
            dif_y, dif_x = ((new_pos[0] - old_pos[0]) * ConfigData().board_step,
                            (new_pos[1] - old_pos[1]) * ConfigData().board_step)
            fig = PlayerData().board_data[old_pos[0]][old_pos[1]]
            Figure.play_anim(fig, fig.pos(), (int(fig.pos().x() + dif_x), int(fig.pos().y() + dif_y)))

            if PlayerData().board_data[kill_pos[0]][kill_pos[1]] != '.':
                del_fig = PlayerData().board_data[kill_pos[0]][kill_pos[1]]
                self.ui.view.graph_scene.removeItem(del_fig)
                PlayerData().board_data[kill_pos[0]][kill_pos[1]] = '.'

            PlayerData().board_data[new_pos[0]][new_pos[1]] = PlayerData().board_data[old_pos[0]][old_pos[1]]
            PlayerData().board_data[old_pos[0]][old_pos[1]] = '.'
            fig.grid_pos = new_pos
        except:
            print_exception()

    def transform_fig(self, kind, grid_pos):
        pieces = {'Queen': Queen, 'Rook': Rook, 'Bishop': Bishop, 'Horse': Horse}
        old_fig = PlayerData().board_data[grid_pos[0]][grid_pos[1]]
        new_fig = pieces[kind](f'icons/figures/{kind}_{old_fig.side[0]}.svg', old_fig.side, kind, grid_pos)
        PlayerData().board_data[grid_pos[0]][grid_pos[1]] = new_fig
        self.ui.view.graph_scene.removeItem(old_fig)
        self.ui.view.graph_scene.addItem(new_fig)

    def mark_last_move(self, res):
        PlayerData().last_figure = PlayerData().board_data[res['new_pos'][0]][res['new_pos'][1]]
        for mark in PlayerData().last_move_marks:
            self.ui.view.graph_scene.removeItem(mark)
        PlayerData().last_move_marks = []
        for pos in ['old_pos', 'new_pos']:
            PlayerData().last_move_marks.append(Mark(f'icons/opt/last_move.svg',
                                                     'last_move', 'default', res[pos]))
            self.ui.view.graph_scene.addItem(PlayerData().last_move_marks[-1])

    def check_handler(self, king_safe, king_under_check, side):
        try:
            if king_safe.check:
                self.remove_check(king_safe)
            if Figure.get_attacks_on(king_under_check.grid_pos, side):
                self.draw_check(king_under_check)
                self.game_end_handler()
        except:
            print_exception()

    def draw_check(self, king):
        mark = Mark(f'icons/opt/king.svg', 'check', 'default', king.grid_pos)
        king.check = mark
        self.ui.view.graph_scene.addItem(mark)

    def remove_check(self, king):
        self.ui.view.graph_scene.removeItem(king.check)
        king.check = None

    def game_end_handler(self):
        try:
            self_figures = PlayerData().get_side_figures(PlayerData().side)
            enemy_figures = PlayerData().get_side_figures(PlayerData().enemy_side)
            self_any_actions, enemy_any_actions = False, False

            for fig in self_figures:
                if self_any_actions:
                    break
                moves, attacks = fig.get_actions(is_protected_check=False)
                for action in moves + attacks:
                    if fig.king_is_safe(PlayerData().side, fig.grid_pos, (action['y'], action['x'])):
                        self_any_actions = True
                        break

            for fig in enemy_figures:
                if enemy_any_actions:
                    break
                moves, attacks = fig.get_actions(is_protected_check=False)
                for action in moves + attacks:
                    if fig.king_is_safe(PlayerData().enemy_side, fig.grid_pos, (action['y'], action['x'])):
                        enemy_any_actions = True
                        break

            if PlayerData().king.check and not self_any_actions:
                game_end_text = GameEndText('LOSE')
                self.ui.view.graph_scene.addItem(game_end_text)
            if PlayerData().enemy_king.check and not enemy_any_actions:
                game_end_text = GameEndText('WIN')
                self.ui.view.graph_scene.addItem(game_end_text)

        except:
            print_exception()