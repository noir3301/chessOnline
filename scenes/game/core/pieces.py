from scenes.game.core.figure import Figure
from communication.global_data import ConfigData, NetworkData, PlayerData


class Pawn(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_actions(self, is_protected_check=False):
        moves, attacks = (), ()
        all_pos = PlayerData().get_all_pos()
        if PlayerData().side == self.side:
            step = - 1
        else:
            step = 1
        y, x = self.grid_pos[0] + step, self.grid_pos[1]
        y_super = y + step

        if 0 <= y < 8 and 0 <= x < 8 and (y, x) not in all_pos:
            moves += {'y': y, 'x': x, 'kind': 'default'},
            if 0 <= y_super < 8 and self.grid_pos[0] == 6 and (y_super, x) not in all_pos:
                moves += {'y': y_super, 'x': x, 'kind': 'default'},
        if (0 <= y < 8 and 0 <= (x - 1) < 8 and
                (PlayerData().board_data[y][x - 1] != '.' and self.side != PlayerData().board_data[y][x - 1].side or
                 is_protected_check)):
            attacks += {'y': y, 'x': x - 1, 'kind': 'default'},
        if (0 <= y < 8 and 0 <= (x + 1) < 8 and
                (PlayerData().board_data[y][x + 1] != '.' and self.side != PlayerData().board_data[y][x + 1].side or
                 is_protected_check)):
            attacks += {'y': y, 'x': x + 1, 'kind': 'default'},

        passing = self.get_passing(y)
        if passing:
            attacks += passing
        return moves, attacks

    def get_passing(self, y_attack):
        passing = ()
        if PlayerData().last_figure and PlayerData().last_move_marks:
            if PlayerData().last_figure.kind == 'Pawn' and abs(
                    PlayerData().last_move_marks[0].grid_pos[0] - PlayerData().last_move_marks[1].grid_pos[0]) == 2:
                if self.grid_pos[0] == PlayerData().last_figure.grid_pos[0] and abs(
                        self.grid_pos[1] - PlayerData().last_figure.grid_pos[1]) == 1:
                    passing += {'y': y_attack, 'x': PlayerData().last_figure.grid_pos[1], 'kind': 'passing'},
        return passing


class Rook(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_actions(self, is_protected_check=False):
        moves, attacks = self.get_lines(is_protected_check)
        return moves, attacks

    @staticmethod
    def castling(king_x):
        old_x = [0, 7][king_x > 7 - king_x]
        rook = PlayerData().board_data[7][old_x]
        rook_dir = 1 if old_x == 0 else -1
        new_x = king_x + rook_dir
        rook.play_anim(rook, rook.pos(), (int(new_x * ConfigData().board_step), int(rook.pos().y())))
        PlayerData().board_data[7][new_x] = rook
        PlayerData().board_data[7][old_x] = '.'
        rook.grid_pos = (7, new_x)
        NetworkData().client.send_turn(PlayerData().side, (7, old_x), (7, new_x), (7, new_x), 0)


class Bishop(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_actions(self, is_protected_check=False):
        moves, attacks = self.get_diags(is_protected_check)
        return moves, attacks


class Queen(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_actions(self, is_protected_check=False):
        line_moves, line_attacks = self.get_lines(is_protected_check)
        diag_moves, diag_attacks = self.get_diags(is_protected_check)
        moves = line_moves + diag_moves
        attacks = line_attacks + diag_attacks
        return moves, attacks


class King(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check = None

    def get_actions(self, is_protected_check=False):
        moves = ()
        attacks = ()
        offsets = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1))
        all_pos = PlayerData().get_all_pos()
        for offset in offsets:
            y, x = offset[0] + self.grid_pos[0], offset[1] + self.grid_pos[1]
            if 0 <= y < 8 and 0 <= x < 8:
                if (y, x) not in all_pos:
                    moves += {'y': y, 'x': x, 'kind': 'default'},
                elif (PlayerData().board_data[y][x] != '.' and self.side != PlayerData().board_data[y][x].side
                      or is_protected_check):
                    attacks += {'y': y, 'x': x, 'kind': 'default'},

        castling = self.get_castling()
        if castling:
            moves += castling
        return moves, attacks

    def get_castling(self):
        castling = ()
        if self.is_first_move:
            y, x = self.grid_pos
            if (PlayerData().board_data[y][7] != '.' and PlayerData().board_data[y][7].kind == 'Rook' and
                    PlayerData().board_data[y][7].side == PlayerData().side and
                    set(PlayerData().board_data[y][x + 1:7]) == {'.'} and PlayerData().board_data[y][7].is_first_move):
                castling += {'y': y, 'x': x + 2, 'kind': 'castling'},
            if (PlayerData().board_data[y][0] != '.' and PlayerData().board_data[y][0].kind == 'Rook' and
                    PlayerData().board_data[y][0].side == PlayerData().side and
                    set(PlayerData().board_data[y][1:x]) == {'.'} and PlayerData().board_data[y][0].is_first_move):
                castling += {'y': y, 'x': x - 2, 'kind': 'castling'},
        return castling

    def castling_is_safe(self, cur_pos, cast_pos):
        cur_y, cur_x = cur_pos
        cast_y, cast_x = cast_pos
        step = -1 if cast_x < cur_x else 1
        for x_king in range(cur_x, cast_x + step, step):
            if not self.king_is_safe(PlayerData().side, (cur_y, cur_x), (cast_y, x_king)):
                return False
        return True


class Horse(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_actions(self, is_protected_check=False):
        moves = ()
        attacks = ()
        offsets = ((-1, -2), (-2, -1), (1, 2), (2, 1), (-1, 2), (1, -2), (-2, 1), (2, -1))
        all_pos = PlayerData().get_all_pos()
        for offset in offsets:
            y, x = offset[0] + self.grid_pos[0], offset[1] + self.grid_pos[1]
            if 0 <= y < 8 and 0 <= x < 8:
                if (y, x) not in all_pos:
                    moves += {'y': y, 'x': x, 'kind': 'default'},
                elif (PlayerData().board_data[y][x] != '.' and self.side != PlayerData().board_data[y][x].side
                      or is_protected_check):
                    attacks += {'y': y, 'x': x, 'kind': 'default'},
        return moves, attacks