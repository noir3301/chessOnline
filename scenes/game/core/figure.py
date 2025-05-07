from PyQt6.QtCore import *
from PyQt6.QtSvgWidgets import *
from communication.global_data import PlayerData, NetworkData, ConfigData, ReferenceData
from utils import print_exception, Logger


class Figure(QGraphicsSvgItem):

    def __init__(self, file_name, side, kind, grid_pos, *args, **kwargs):
        super().__init__(file_name, *args, **kwargs)
        self.installEventFilter(self)
        self.setScale(ConfigData().board_step / 512)
        self.is_selected: bool = False
        self.is_first_move: bool = True
        self.kind: str = ''
        self.side: str = ''
        self.grid_pos: tuple = ()
        self.clicked_count = 0
        self.setZValue(2)
        self.side, self.kind, self.grid_pos = side, kind, grid_pos
        self.moveBy(grid_pos[1]*ConfigData().board_step, grid_pos[0]*ConfigData().board_step)

    def get_lines(self, is_protected_check):
        moves = ()
        attacks = ()
        all_pos = PlayerData().get_all_pos()
        ranges = (range(self.grid_pos[0] - 1, -1, -1), range(self.grid_pos[0] + 1, 8, 1),
                  range(self.grid_pos[1] - 1, -1, -1), range(self.grid_pos[1] + 1, 8, 1))
        for n in range(4):
            for coord in ranges[n]:
                if n < 2:
                    if (coord, self.grid_pos[1]) not in all_pos:
                        moves += {'y': coord, 'x': self.grid_pos[1], 'kind': 'default'},
                    else:
                        if self.side != PlayerData().board_data[coord][self.grid_pos[1]].side or is_protected_check:
                            attacks += {'y': coord, 'x': self.grid_pos[1], 'kind': 'default'},
                        break
                elif n >= 2:
                    if (self.grid_pos[0], coord) not in all_pos:
                        moves += {'y': self.grid_pos[0], 'x': coord, 'kind': 'default'},
                    else:
                        if self.side != PlayerData().board_data[self.grid_pos[0]][coord].side or is_protected_check:
                            attacks += {'y': self.grid_pos[0], 'x': coord, 'kind': 'default'},
                        break
        return moves, attacks

    def get_diags(self, is_protected_check):
        moves = ()
        attacks = ()
        all_pos = PlayerData().get_all_pos()
        ranges = ((range(self.grid_pos[0] - 1, -1, -1), range(self.grid_pos[1] - 1, -1, -1)),
                  (range(self.grid_pos[0] + 1, 8), range(self.grid_pos[1] + 1, 8)),
                  (range(self.grid_pos[0] - 1, -1, -1), range(self.grid_pos[1] + 1, 8)),
                  (range(self.grid_pos[0] + 1, 8), range(self.grid_pos[1] - 1, -1, -1)))
        for n in range(4):
            for y, x in zip(ranges[n][0], ranges[n][1]):
                if (y, x) not in all_pos:
                    moves += {'y': y, 'x': x, 'kind': 'default'},
                else:
                    if self.side != PlayerData().board_data[y][x].side or is_protected_check:
                        attacks += {'y': y, 'x': x, 'kind': 'default'},
                    break
        return moves, attacks

    @staticmethod
    def get_attacks_on(grid_pos, on_side):
        y, x = grid_pos
        attacks_on = ()
        for row in PlayerData().board_data:
            for fig in row:
                if fig != '.' and fig.side != on_side:
                    moves, attacks = fig.get_actions(is_protected_check=True)
                    for attack in attacks:
                        if attack == {'y': y, 'x': x, 'kind': 'default'}:
                            attacks_on += {'y': y, 'x': x, 'kind': 'default'},
                    for move in moves:
                        if move == {'y': y, 'x': x, 'kind': 'default'}:
                            attacks_on += {'y': y, 'x': x, 'kind': 'default'},
        Logger().write_info({'descr': 'attacks on pos', 'on_pos': grid_pos, 'attacks': attacks_on})
        return attacks_on

    def draw_actions(self):
        try:
            moves, attacks = self.get_actions(is_protected_check=False)
            Logger().write_info({'descr': 'figure actions', 'fig': self, 'moves': moves, 'attacks': attacks})
            action = Mark('icons/opt/select.svg', 'select', 'default', self.grid_pos)
            cur_y, cur_x = self.grid_pos[0], self.grid_pos[1]
            PlayerData().board_marks.append(action)
            ReferenceData().game_ui.view.graph_scene.addItem(action)

            for actions, kind in zip((moves, attacks), ('move', 'attack')):
                for action in actions:
                    if action:
                        y, x, subkind = action.values()
                        if self.king_is_safe(PlayerData().side, (cur_y, cur_x), (y, x)):
                            if subkind != 'castling' or self.castling_is_safe((cur_y, cur_x), (y, x)):
                                mark = Mark(f'icons/opt/{kind}.svg', kind, subkind,(y, x))
                                PlayerData().board_marks.append(mark)
                                ReferenceData().game_ui.view.graph_scene.addItem(mark)
        except:
            print_exception()

    def mousePressEvent(self, event):  # FIGURE SELECT HANDLER
        try:
            if PlayerData().side == self.side and event.button() == Qt.MouseButton.LeftButton and PlayerData().turn:
                self.clicked_count = self.clicked_count + 1
                if not self.is_selected:
                    Mark.remove_marks()
                    self.is_selected = True
                    if PlayerData().last_selected_figure and PlayerData().last_selected_figure != self:
                        PlayerData().last_selected_figure.is_selected = False
                        PlayerData().last_selected_figure.clicked_count = 0
                    PlayerData().last_selected_figure = self
                    self.draw_actions()
        except:
            print_exception()
        super(Figure, self).mousePressEvent(event)

    def eventFilter(self, widget, event):  # MOVE BY DRAG HANDLER
        try:
            str_event = str(event.type())
            if '157' == str_event and event.button() == Qt.MouseButton.LeftButton:
                new_grid_pos = (round(self.pos().y() / ConfigData().board_step),
                                round(self.pos().x() / ConfigData().board_step))
                new_y, new_x = new_grid_pos
                old_y, old_x = self.grid_pos
                valid_action = Mark.get_by_pos(new_grid_pos)

                if valid_action and valid_action.kind in ('move', 'attack'):
                    self.setPos(new_x * ConfigData().board_step, new_y * ConfigData().board_step)
                    kill_pos = self.data_update(valid_action.kind, valid_action.subkind, new_grid_pos)
                    self.buffer_clear()
                    is_swap = self.special_action_handler(valid_action.subkind, new_grid_pos)
                    NetworkData().client.send_turn(PlayerData().side, (old_y, old_x), new_grid_pos, kill_pos, is_swap)
                else:
                    self.setPos(self.grid_pos[1] * ConfigData().board_step, self.grid_pos[0] * ConfigData().board_step)
                if not valid_action or self.clicked_count == 2:
                    self.buffer_clear()
        except:
            print_exception()
        return super().eventFilter(widget, event)

    def play_action(self, kind, subkind):  # MOVE BY CLICK HANDLER
        try:
            dif_y, dif_x = ((PlayerData().last_selected_mark[0] - self.grid_pos[0]) * ConfigData().board_step,
                            (PlayerData().last_selected_mark[1] - self.grid_pos[1]) * ConfigData().board_step)
            old_y, old_x = self.grid_pos
            new_y, new_x = PlayerData().last_selected_mark[0], PlayerData().last_selected_mark[1]
            self.play_anim(self, self.pos(), (int(self.pos().x() + dif_x), int(self.pos().y() + dif_y)))
            kill_pos = self.data_update(kind, subkind, (new_y, new_x))
            self.buffer_clear()
            is_swap = self.special_action_handler(subkind, (new_y, new_x))
            NetworkData().client.send_turn(PlayerData().side, (old_y, old_x), (new_y, new_x), kill_pos, is_swap)
        except:
            print_exception()

    def special_action_handler(self, subkind, cur_pos, is_swap = 1):
        cur_y, cur_x = cur_pos
        if self.kind == 'Pawn' and cur_y == 0:  # pawn transform
            is_swap = 0
            PlayerData().transforming_pawn = self
            ReferenceData().game_choice_cls.show_choices()
        elif subkind == 'castling':
            rook_x = [0, 7][cur_x > 7 - cur_x]
            rook = PlayerData().board_data[7][rook_x]
            rook.castling(cur_x)
        return is_swap

    def king_is_safe(self, on_side, cur_pos, move_pos):
        if on_side == PlayerData().side:
            king = PlayerData().king
        else:
            king = PlayerData().enemy_king
        cur_y, cur_x = cur_pos
        move_y, move_x = move_pos
        fig, target = PlayerData().board_data[cur_y][cur_x], PlayerData().board_data[move_y][move_x]
        PlayerData().board_data[cur_y][cur_x], PlayerData().board_data[move_y][move_x] = '.', fig
        self.grid_pos = (move_y, move_x)
        attacks_on_king = self.get_attacks_on(king.grid_pos, on_side)
        self.grid_pos = (cur_y, cur_x)
        PlayerData().board_data[cur_y][cur_x], PlayerData().board_data[move_y][move_x] = fig, target
        return not attacks_on_king

    @staticmethod
    def play_anim(fig, start, end):
        anim = QPropertyAnimation(fig, b"pos", fig)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.setDuration(250)
        anim.setStartValue(start)
        anim.setEndValue(QPoint(end[0], end[1]))
        anim.start()

    def data_update(self, kind, subkind, new_pos):
        try:
            PlayerData().turn = False
            kill_pos = new_pos
            y_old, x_old = self.grid_pos
            y_new, x_new = new_pos
            acting_fig = PlayerData().board_data[y_old][x_old]
            if kind == 'attack':
                if subkind == 'passing':
                    kill_pos = (y_new+1, x_new)
                ReferenceData().game_ui.view.graph_scene.removeItem(PlayerData().board_data[kill_pos[0]][kill_pos[1]])
                print(kill_pos)
                PlayerData().board_data[kill_pos[0]][kill_pos[1]] = '.'
            PlayerData().board_data[y_old][x_old] = '.'
            PlayerData().board_data[y_new][x_new] = acting_fig
            self.grid_pos = new_pos
            self.is_first_move = False
        except:
            print_exception()
        return kill_pos

    def buffer_clear(self):
        self.is_selected, self.clicked_count = False, 0
        PlayerData().last_selected_mark, PlayerData().last_selected_figure = None, None
        Mark.remove_marks()


class Mark(QGraphicsSvgItem):
    def __init__(self, file_name, kind, subkind, grid_pos, *args, **kwargs):
        super().__init__(file_name, *args, **kwargs)
        self.setScale(ConfigData().board_step / 100)
        self.grid_pos = grid_pos
        self.kind = kind
        self.subkind = subkind
        self.setZValue(1)
        self.setPos(grid_pos[1]*ConfigData().board_step, grid_pos[0]*ConfigData().board_step)

    def mousePressEvent(self, event):
        if PlayerData().last_selected_figure and self.kind in ('move', 'attack'):
            PlayerData().last_selected_mark = self.grid_pos
            PlayerData().last_selected_figure.play_action(self.kind, self.subkind)
        super(Mark, self).mousePressEvent(event)

    @staticmethod
    def remove_marks():
        for mark in PlayerData().board_marks:
            ReferenceData().game_ui.view.graph_scene.removeItem(mark)
        PlayerData().board_marks.clear()

    @staticmethod
    def get_by_pos(grid_pos):
        for action in PlayerData().board_marks:
            if action.grid_pos == grid_pos:
                return action