from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import *
from scenes.game.core.pieces import Pawn, Rook, Horse, Bishop, Queen, King
from communication.global_data import PlayerData, NetworkData, ConfigData, ReferenceData
from utils import print_exception


class UI(QFrame):

    def __init__(self, *args):
        super().__init__(*args)
        ReferenceData().game_ui = self
        ReferenceData().game_choice_cls = Choice
        self.set_style_sheet()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nickname_boxes = {'top': NicknameBox(), 'bottom': NicknameBox()}
        self.view = View()
        self.layout.addWidget(self.nickname_boxes['top'])
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.nickname_boxes['bottom'])
        self.setLayout(self.layout)

    def set_style_sheet(self):
        with open('scenes/game/style.qss', 'r') as f:
            _style = f.read()
            self.setStyleSheet(_style)

    def set_nicknames(self):
        self.nickname_boxes['top'].nickname_label.setText(PlayerData().enemy_login)
        self.nickname_boxes['bottom'].nickname_label.setText(PlayerData().login)


class View(QGraphicsView):
    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumSize(*ConfigData().view_size)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_scene = Scene(0, 0, ConfigData().graph_scene_size[0], ConfigData().graph_scene_size[1])
        self.setScene(self.graph_scene)


class Scene(QGraphicsScene):
    def __init__(self, *args):
        super().__init__(*args)
        self.build_board()

    def build_board(self):
        for i in range(8):
            for j in range(8):
                square_cur = PlayerData().squares[(i + j) % 2 == 0]
                square = QGraphicsSvgItem(square_cur)
                square.setScale(ConfigData().board_step * 0.01)
                square.moveBy(i * ConfigData().board_step, j * ConfigData().board_step)
                self.addItem(square)

    def build_figures(self):
        pieces = {'Pawn': Pawn, 'Rook': Rook, 'Bishop': Bishop, 'Horse': Horse, 'Queen': Queen, 'King': King}
        sides_dict = {'w': 'white', 'b': 'black'}
        if PlayerData().side == 'white':
            PlayerData().board_data = PlayerData().init_board_w
        elif PlayerData().side == 'black':
            PlayerData().board_data = PlayerData().init_board_b
        for i in range(8):
            for j in range(8):
                if PlayerData().board_data[i][j] != '.':
                    name = PlayerData().board_data[i][j]
                    kind, side = name[:-2], sides_dict[name[-1]]
                    fig = pieces[kind](f'icons/figures/{name}.svg', side, kind, (i, j))
                    if fig.side == PlayerData().side:
                        fig.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                        if fig.kind == 'King':
                            PlayerData().king = fig
                    if fig.kind == 'King' and fig.side != PlayerData().side:
                        PlayerData().enemy_king = fig
                    PlayerData().board_data[i][j] = fig
                    self.addItem(fig)

    def build_transform_pad(self):
        kinds = ('Queen', 'Rook', 'Bishop', 'Horse')
        scene_x, scene_y = ConfigData().graph_scene_size
        start_x = ConfigData().board_step*2
        for i, kind in enumerate(kinds):
            ch_btn = Choice(kind)
            icon = QIcon(f"icons/figures/{kind}_{PlayerData().side[0]}.svg")
            ch_btn.setIcon(icon)
            ch_btn.move(start_x + ConfigData().board_step * i, scene_y // 2 - ConfigData().board_step // 2)
            self.addWidget(ch_btn)


class Choice(QPushButton):
    choices = []

    def __init__(self, kind, *args):
        super().__init__(*args)
        self.kind = kind
        self.setFixedSize(ConfigData().board_step, ConfigData().board_step)
        size = QSize(ConfigData().board_step-20, ConfigData().board_step-20)
        self.setIconSize(size)
        Choice.choices.append(self)
        self.setDisabled(True)
        self.setHidden(True)

    def mousePressEvent(self, event):
        try:
            pawn = PlayerData().transforming_pawn
            self.hide_choices()
            pieces = {'Queen': Queen, 'Rook': Rook, 'Bishop': Bishop, 'Horse': Horse}
            new_fig = pieces[self.kind](f'icons/figures/{self.kind}_{pawn.side[0]}.svg', pawn.side, self.kind, pawn.grid_pos)
            new_fig.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            PlayerData().board_data[new_fig.grid_pos[0]][new_fig.grid_pos[1]] = new_fig
            ReferenceData().game_ui.view.graph_scene.removeItem(pawn)
            ReferenceData().game_ui.view.graph_scene.addItem(new_fig)
            PlayerData().transforming_pawn = None
            NetworkData().client.send_transform(PlayerData().side, new_fig.kind, new_fig.grid_pos, 1)
        except Exception:
            print_exception()

    @classmethod
    def show_choices(cls):
        for choice in cls.choices:
            choice.setHidden(False)
            choice.setDisabled(False)
            cls.set_figures_z(0)

    @classmethod
    def hide_choices(cls):
        for choice in cls.choices:
            choice.setDisabled(True)
            choice.setHidden(True)
            cls.set_figures_z(2)

    @staticmethod
    def set_figures_z(z_value):
        for y in (3, 4):
            for x in (2, 3, 4, 5):
                if PlayerData().board_data[y][x] != '.':
                    PlayerData().board_data[y][x].setZValue(z_value)


class NicknameBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nickname_label = NicknameLabel('')
        self.profile_svg = ProfileSvg()
        self.layout.addWidget(self.nickname_label)
        self.layout.addWidget(self.profile_svg)
        self.setLayout(self.layout)

    def set_nickname(self, nickname):
        self.nickname_label.setText(nickname)


class NicknameLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)


class ProfileSvg(QSvgWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.load('icons/profile.svg')
        self.setFixedSize(25, 25)


class GameEndText(QGraphicsTextItem):
    def __init__(self, text, *args):
        super().__init__(*args)
        self.setZValue(3)
        self.setPlainText(text)
        self.setDefaultTextColor(QColor(0, 0, 0, 180))
        font = QFont("Helvetica [Cronyx]", ConfigData().graph_scene_size[0] // 7)
        font.setBold(True)
        self.setFont(font)
        bounding_rect = self.boundingRect()
        x = ConfigData().graph_scene_size[0] // 2 - bounding_rect.width() // 2
        y = ConfigData().graph_scene_size[1] // 2 - bounding_rect.height() // 2
        self.setPos(x, y)





