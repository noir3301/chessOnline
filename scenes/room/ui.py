from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class UI(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_box = MainBox()
        self.layout.addWidget(self.main_box)
        self.set_style_sheet()
        self.setLayout(self.layout)

    def set_style_sheet(self):
        with open('scenes/room/style.qss', 'r') as f:
            _style = f.read()
            self.setStyleSheet(_style)


class MainBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFixedSize(460, 450)
        self.layout = QVBoxLayout()
        self.slots_ins = {0: SlotBox(), 1: SlotBox()}
        self.layout.addWidget(self.slots_ins[0])
        self.layout.addWidget(self.slots_ins[1])
        self.warning_box = WarningBox()
        self.layout.addWidget(self.warning_box)
        self.setLayout(self.layout)


class WarningBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumHeight(30)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.warning_label = WarningLabel()
        self.layout.addWidget(self.warning_label)
        self.setLayout(self.layout)


class SlotBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(150)
        self.player_box = PlayerBox()
        self.layout.addWidget(self.player_box)
        self.setLayout(self.layout)


class PlayerBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumHeight(150)
        self.layout = QGridLayout(self)
        self.login_label = LoginLabel()
        self.choice_box = ChoiceBox()
        self.ready_btn = ReadyButton('Ready')
        self.layout.addWidget(self.login_label, 0, 0)
        self.layout.addWidget(self.choice_box, 1, 0)
        self.layout.addWidget(self.ready_btn, 1, 1)
        self.setHidden(True)
        self.setLayout(self.layout)


class ChoiceBox(QFrame):
    BOUND_FUNC = None

    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QHBoxLayout()
        self.choices = {'white': ChoiceButton('icons/figures/King_w.svg', 'white'),
                        'black': ChoiceButton('icons/figures/King_b.svg', 'black'),
                        'random': ChoiceButton('icons/figures/King_r.svg', 'random')}
        self.cur_choice = None
        self.layout.addWidget(self.choices['white'])
        self.layout.addWidget(self.choices['black'])
        self.layout.addWidget(self.choices['random'])
        self.setLayout(self.layout)

    def disable_choices(self):
        for choice in self.choices.values():
            choice.setDisabled(True)

    def enable_choices(self):
        for choice in self.choices.values():
            choice.setDisabled(False)
            choice.clicked.connect(self.choice_clicked)

    def choice_clicked(self):
        target = self.sender()
        for choice in self.choices.values():
            if choice != target:
                choice.selected = False
                choice.clear_border()
            else:
                choice.selected = True
                self.cur_choice = choice
                choice.set_border()
                ChoiceBox.BOUND_FUNC(choice.kind)
                self.parent().ready_btn.setDisabled(False)

class ChoiceButton(QPushButton):
    def __init__(self, icon, kind, *args):
        super().__init__(*args)
        self.kind = kind
        self.selected = False
        self.setFixedSize(70, 70)
        size = QSize(60, 60)
        self.setIconSize(size)
        self.setIcon(QIcon(icon))
        self.setDisabled(True)

    def set_border(self):
        self.setStyleSheet('border: None; border-top: 5px solid #dec496; background-color: #ded8ce;')

    def clear_border(self):
        self.setStyleSheet(':default border: 1px solid black; background-color: transparent;')


class ReadyButton(QPushButton):
    BOUND_FUNC = None
    CHECK_READY = None

    def __init__(self, *args):
        super().__init__(*args)
        self.setMinimumHeight(45)
        self.setMaximumWidth(160)
        self.setDisabled(True)
        self.clicked_flag = False
        self.clicked.connect(self.click_ev)

    def click_ev(self):
        target = self.sender()
        self.clicked_flag = True
        target.setDisabled(True)
        self.parent().choice_box.disable_choices()
        self.set_ready_style()
        ReadyButton.BOUND_FUNC()

    def set_ready_style(self):
        self.setStyleSheet('background-color: #7fe15f;')


class LoginLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)
        self.setMaximumHeight(30)

    def set_login(self, login):
        self.setText(login)

class WarningLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)