from utils import Singleton


class ConfigData(metaclass=Singleton):
    def __init__(self):
        self.default_port = '65455'
        self.board_step = 75
        self.main_win_size = (800, 750)
        self.view_size = (self.main_win_size[0] - 100, self.main_win_size[1] - 50)
        self.graph_scene_size = (self.view_size[0] - 100, self.view_size[1] - 100)


class PlayerData(metaclass=Singleton):
    def __init__(self):
        self.login = ''
        self.enemy_login = ''
        self.room_slot = None
        self.side, self.enemy_side = None, None
        self.king, self.enemy_king = None, None
        self.transforming_pawn = None
        self.turn = False
        self.board_marks = []
        self.last_move_marks = []
        self.last_figure = None
        self.last_selected_mark = None
        self.last_selected_figure = None
        self.squares = ['icons/board_squares/Black_square.svg', 'icons/board_squares/White_square.svg']
        self.init_board_w = [['Rook_b', 'Horse_b', 'Bishop_b', 'Queen_b', 'King_b', 'Bishop_b', 'Horse_b', 'Rook_b'],
                            ['Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w'],
                            ['Rook_w', 'Horse_w', 'Bishop_w', 'Queen_w', 'King_w', 'Bishop_w', 'Horse_w', 'Rook_w']]
        self.init_board_b = [['Rook_w', 'Horse_w', 'Bishop_w', 'King_w', 'Queen_w', 'Bishop_w', 'Horse_w', 'Rook_w'],
                            ['Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w', 'Pawn_w'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['.', '.', '.', '.', '.', '.', '.', '.'],
                            ['Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b', 'Pawn_b'],
                            ['Rook_b', 'Horse_b', 'Bishop_b', 'King_b', 'Queen_b', 'Bishop_b', 'Horse_b', 'Rook_b']]
        self.board_data = [[], [], [], [], [], [], [], []]

    def get_all_pos(self):
        all_pos = ()
        for row in self.board_data:
            for el in row:
                if el != '.':
                    all_pos += el.grid_pos,
        return all_pos

    def get_side_figures(self, side):
        figures = ()
        for row in self.board_data:
            for el in row:
                if el != '.' and el.side == side:
                    figures += (el,)
        return figures


class NetworkData(metaclass=Singleton):
    def __init__(self):
        self.client = None
        self.client_thread = None
        self.irc_client = None
        self.irc_connect_event = None   # MAY BE NOT GLOBAL???
        self.irc_stop_event = None


        self.serv = None
        self.serv_ip = None
        self.serv_port = None
        self.serv_process = None
        self.serv_stop_event = None


class ReferenceData(metaclass=Singleton):
    def __init__(self):
        self.auth_ui = None
        self.menu_ui = None
        self.room_ui = None
        self.game_ui = None
        self.game_choice_cls = None