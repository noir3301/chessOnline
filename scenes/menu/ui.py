from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtTest import QTest
from utils import add_widgets, Validation, get_local_ip, get_public_ip


class UI(QFrame):

    def __init__(self, *args):
        super().__init__(*args)
        self.main_box = MainBox()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.main_box)
        self.set_style_sheet()
        self.setLayout(self.layout)

    def set_style_sheet(self):
        with open('scenes/menu/style.qss', 'r') as f:
            _style = f.read()
            self.setStyleSheet(_style)


class MainBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFixedSize(600, 600)
        self.layout = QVBoxLayout()
        self.top_box = TopBox()
        self.rooms_box = RoomsBox()
        self.join_box = JoinBox()
        self.create_box = CreateBox()
        self.warning_box = WarningBox()
        widgets = (self.top_box, self.rooms_box, self.join_box, self.create_box, self.warning_box)
        add_widgets(self.layout, widgets)
        self.setLayout(self.layout)


class TopBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumHeight(50)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.irc_hint = IRCLabel('IRC (WIP)')
        self.load_box = LoadBox()
        self.slider = Slider((65, 40))
        self.login_label = LoginLabel()
        add_widgets(self.layout, (self.irc_hint, self.slider, self.load_box, self.login_label))
        self.setLayout(self.layout)


class LoadBox(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.setStyleSheet('border: None;')
        self.view.setStyleSheet('border: None; background-color: transparent;')
        self.setFixedSize(50, 30)
        self.view.setFixedSize(50, 30)
        self.scene.setSceneRect(0, 0, 45, 25)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(0, 0, 0), 3, Qt.PenStyle.SolidLine)
        brush = QBrush(QColor(0, 0, 0), Qt.BrushStyle.SolidPattern)
        self.p1 = QGraphicsEllipseItem(10, 12, 3, 3)
        self.p2 = QGraphicsEllipseItem(20, 12, 3, 3)
        self.p3 = QGraphicsEllipseItem(30, 12, 3, 3)
        self.p1.setPen(pen), self.p1.setBrush(brush)
        self.p2.setPen(pen), self.p2.setBrush(brush)
        self.p3.setPen(pen), self.p3.setBrush(brush)
        self.p1.setOpacity(0), self.p2.setOpacity(0), self.p3.setOpacity(0)
        self.view.setScene(self.scene)
        self.scene.addItem(self.p1), self.scene.addItem(self.p2), self.scene.addItem(self.p3)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

    def anim_play(self, stop_event):
        ps = [self.p1, self.p2, self.p3]
        list = [2, 0, 1]
        count = 0
        [p.setOpacity(0.2) for p in ps]
        while True:
            for i in range(0, 5):
                for j, p in enumerate(ps):
                    for k in range(3, 11):
                        op = k / 10
                        p.setOpacity(op)
                        if count > 0:
                            ps[list[j]].setOpacity(1.2 - op)
                        self.update()
                        if stop_event.is_set():
                            self.p1.setOpacity(0), self.p2.setOpacity(0), self.p3.setOpacity(0)
                            self.update()
                            return
                        QTest.qWait(50)
                    count += 1
                    QTest.qWait(50)


class RoomsBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QHBoxLayout()
        self.rooms_list = RoomsList()
        self.layout.addWidget(self.rooms_list)
        self.setLayout(self.layout)


class JoinBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumHeight(45)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        self.ip_port_input = Input((180, 40), 'ip_port', 'IP:PORT', '')
        self.paste_box = JoinPasteBox(self.ip_port_input)
        self.confirm_btn = ConfirmButton((180, 40), 'join', self.ip_port_input, 'Join room')
        add_widgets(self.layout, (self.paste_box, self.ip_port_input, self.confirm_btn))
        self.setLayout(self.layout)


class CreateBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumHeight(45)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        self.ip_port_input = Input((180, 40), 'ip_port', 'IP:PORT', '')
        self.paste_box = CreatePasteBox(self.ip_port_input)
        self.confirm_btn = ConfirmButton((180, 40), 'create', self.ip_port_input, 'Create room')
        add_widgets(self.layout, (self.paste_box, self.ip_port_input, self.confirm_btn))
        self.setLayout(self.layout)


class JoinPasteBox(QFrame):
    def __init__(self, paste_target, *args):
        super().__init__(*args)
        self.setMaximumHeight(40)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        self.local = PasteButton((40, 18), 'local', paste_target, 'local')
        self.layout.addWidget(self.local)
        self.setLayout(self.layout)


class CreatePasteBox(QFrame):
    def __init__(self, paste_target, *args):
        super().__init__(*args)
        self.setMaximumHeight(40)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        self.local = PasteButton((40, 18), 'local', paste_target, 'local')
        self.public = PasteButton((40, 18), 'public', paste_target, 'public')
        add_widgets(self.layout, (self.local, self.public))
        self.setLayout(self.layout)


class WarningBox(QFrame):
    WARNING_INSTANCE = None

    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumHeight(30)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.warning_label = WarningLabel()
        WarningBox.WARNING_INSTANCE = self.warning_label
        self.layout.addWidget(self.warning_label)
        self.setLayout(self.layout)


class Slider(QSlider):
    BOUND_FUNC = None
    INSTANCE = None

    def __init__(self, size: tuple, *args):
        super().__init__(*args)
        Slider.INSTANCE = self
        self.setOrientation(Qt.Orientation.Horizontal)
        self.min, self.max = 0, 10
        self.setRange(self.min, self.max)
        self.setValue(0)
        self.is_enabled_irc = False
        self.setFixedSize(*size)
        self.state = 'default'
        self.styles = {
            'default': 'Slider::handle:horizontal { background-color: #8B4513; border: 2px solid #8B4513; }',
            'connected': 'Slider::handle:horizontal { background-color: #759c0f; border: 2px solid #759c0f; }',
            'failed': 'Slider::handle:horizontal { background-color: #eb4444; border: 2px solid #eb4444; }'
        }

    def mousePressEvent(self, ev):
        self.setDisabled(True)
        if self.state == 'failed':
            self.setStyleSheet(self.styles['default'])
        self.anim_play()
        Slider.BOUND_FUNC(self.is_enabled_irc)

    def keyPressEvent(self, *args, **kwargs):
        pass

    def set_state(self, state):
        self.state = state
        if self.state in self.styles.keys():
            self.setStyleSheet(self.styles[state])
            if self.state == 'connected':
                self.is_enabled_irc = True
            elif self.state == 'default':
                self.is_enabled_irc = False
            elif self.state == 'failed':
                self.is_enabled_irc = True
                self.anim_play()
                self.is_enabled_irc = False
        self.setDisabled(False)

    def anim_play(self):
        start = self.sliderPosition()
        end, step = [(self.max + 1, 1), (self.min - 1, -1)][self.is_enabled_irc]
        for i in range(start, end, step):
            self.setValue(i)
            self.repaint()
            QTest.qWait(10)


class RoomsList(QListWidget):  ### QTableWidget OR QListWidget OR QListView
    def __init__(self, *args):
        super().__init__(*args)
        self.setFixedSize(500, 380)

    def add_item(self, name):
        self.addItem(name)

class Input(QLineEdit):
    def __init__(self, size: tuple, inp_type, place_holder, text, *args):
        super().__init__(*args)
        self.setFixedSize(*size)
        self.inp_type = inp_type
        self.setPlaceholderText(place_holder)
        self.setText(text)

    def validate_inp(self):
        return Validation.validate(self.inp_type, self.text())


class PasteButton(QPushButton):
    DEFAULT_PORT = 0

    def __init__(self, size: tuple, paste_type, paste_target, *args):
        super().__init__(*args)
        self.setFixedSize(*size)
        self.paste_type = paste_type
        self.paste_target = paste_target
        self.clicked.connect(self.insert_ip)

    def insert_ip(self):
        if self.paste_type == 'local':
            text = f'{get_local_ip()}:{PasteButton.DEFAULT_PORT}'
        elif self.paste_type == 'public':
            text = f'{get_public_ip()}:{PasteButton.DEFAULT_PORT}'
        else:
            return
        if self.paste_target.text() != text:
            self.paste_target.setText(text)
        else:
            self.paste_target.setText('')


class ConfirmButton(QPushButton):
    INSTANCES = []
    BOUND_FUNC = None

    def __init__(self, size: tuple, btn_type, bound_inp, *args):
        super().__init__(*args)
        ConfirmButton.INSTANCES.append(self)
        self.setFixedSize(*size)
        self.btn_type = btn_type
        self.bound_inp = bound_inp
        self.clicked.connect(self.confirm_event)

    def confirm_event(self):
        if Slider.INSTANCE.is_enabled_irc:
            ConfirmButton.BOUND_FUNC('IRC', self.btn_type)
        else:   # if irc disabled
            if Validation.ip_port(self.bound_inp.text()):
                ConfirmButton.set_disabled_all(True)
                ConfirmButton.BOUND_FUNC('IP', self.btn_type, self.bound_inp.text())
            else:
                WarningBox.WARNING_INSTANCE.throw_warn(f'invalid ip:port to {self.btn_type}', 'red')

    @classmethod
    def set_disabled_all(cls, is_disabled: bool):
        [button.setDisabled(is_disabled) for button in cls.INSTANCES]


class WarningLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)

    def throw_warn(self, text, color='#000000'):
        self.setText(text)
        self.setStyleSheet(f'color: {color};')


class IRCLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.setToolTip('Allows to create and join to the lobby of those who have also connected to IRC-network\n'
                        'Disallows creating and joining a lobby using a local and public IP address')


class LoginLabel(QLabel):
    INSTANCE = None

    def __init__(self, *args):
        super().__init__(*args)
        LoginLabel.INSTANCE = self
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    @classmethod
    def login_update(cls, login):
        cls.INSTANCE.setText(login)


