from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
from utils import add_widgets, Validation


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
        with open('scenes/authorization/style.qss', 'r') as f:
            _style = f.read()
            self.setStyleSheet(_style)


class MainBox(QFrame):
    INSTANCE: QFrame = None
    ORIG_FORM: str = 'GuestBox'
    FORMS_CLS: dict = {}
    CUR_FORM: QFrame = None

    def __init__(self, *args):
        super().__init__(*args)
        MainBox.INSTANCE = self
        MainBox.FORMS_CLS = {'SignInBox': SignInBox, 'SignUpBox': SignUpBox, 'GuestBox': GuestBox}
        self.setFixedSize(550, 500)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.switch_box = SwitchBox()
        MainBox.CUR_FORM = MainBox.FORMS_CLS[MainBox.ORIG_FORM]()
        add_widgets(self.layout, (self.switch_box, MainBox.CUR_FORM))
        self.setLayout(self.layout)

    @classmethod
    def switch_auth(cls, new_form: str):
        cls.INSTANCE.layout.removeWidget(cls.CUR_FORM)
        cls.CUR_FORM = cls.FORMS_CLS[new_form]()
        cls.INSTANCE.layout.addWidget(cls.CUR_FORM)


class SwitchBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFixedHeight(140)
        self.layout = QHBoxLayout()
        self.signin_btn = SwitchButton((140, 50), 'SignInBox','Sign In')
        self.signup_btn = SwitchButton((140, 50), 'SignUpBox', 'Sign Up')
        self.guest_btn = SwitchButton((140, 50), 'GuestBox', 'Guest')
        add_widgets(self.layout, (self.signin_btn, self.signup_btn, self.guest_btn))
        self.setLayout(self.layout)


class SignInBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignCenter)
        self.login_hint = HintLabel('login')
        self.login_input = Input((180, 40), 'login', 'login')
        self.password_hint = HintLabel('password')
        self.password_input = Input((180, 40), 'password', 'password')
        self.warning_label = WarningLabel()
        self.confirm_btn = ConfirmButton((180, 50), 'SignInBox', 'Confirm (WIP)')
        widgets = (self.login_hint, self.login_input, self.password_hint,
                   self.password_input, self.warning_label, self.confirm_btn)
        add_widgets(self.layout, widgets)
        self.setLayout(self.layout)


class SignUpBox(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignCenter)
        self.login_hint = HintLabel('login')
        self.login_input = Input((180, 40), 'login', 'login')
        self.password_hint = HintLabel('password')
        self.password_input = Input((180, 40), 'password', 'password')
        self.email_hint = HintLabel('email')
        self.email_input = Input((180, 40), 'email', 'email')
        self.warning_label = WarningLabel()
        self.confirm_btn = ConfirmButton((180, 50), 'SignUpBox', 'Confirm (WIP)')
        widgets = (self.login_hint, self.login_input, self.password_hint, self.password_input,
                   self.email_hint, self.email_input, self.warning_label, self.confirm_btn)
        add_widgets(self.layout, widgets)
        self.setLayout(self.layout)


class GuestBox(QFrame):
    VALIDATION_FIELDS: tuple = ()
    WARNING_INSTANCE: QLabel = None

    def __init__(self, *args):
        super().__init__(*args)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignCenter)
        self.login_hint = HintLabel('nickname')
        self.login_input = Input((180, 40), 'login', 'nickname')
        self.warning_label = WarningLabel()
        self.confirm_btn = ConfirmButton((180, 50), 'GuestBox', 'Confirm')
        GuestBox.VALIDATION_FIELDS = (self.login_input,)
        GuestBox.WARNING_INSTANCE = self.warning_label
        widgets = (self.login_hint, self.login_input, self.warning_label, self.confirm_btn)
        add_widgets(self.layout, widgets)
        self.setLayout(self.layout)

    @classmethod
    def validate_form(cls):
        result = [field.validate_inp() for field in cls.VALIDATION_FIELDS]
        return result


class Input(QLineEdit):
    def __init__(self, size: tuple, inp_type, place_holder, *args):
        super().__init__(*args)
        self.setFixedSize(*size)
        self.inp_type = inp_type
        self.setPlaceholderText(place_holder)

    def validate_inp(self):
        return Validation.validate(self.inp_type, self.text())


class PushButton(QPushButton):
    def __init__(self, size: tuple, *args):
        super().__init__(*args)
        self.setFixedSize(*size)

class SwitchButton(PushButton):
    CUR_BUTTON = None

    def __init__(self, size: tuple, depend_form, *args):
        super().__init__(size, *args)
        self.depend_form = depend_form
        self.clicked.connect(self.switch_event)
        if self.depend_form == MainBox.ORIG_FORM:
            SwitchButton.CUR_BUTTON = self
            self.set_border()

    def switch_event(self):
        SwitchButton.CUR_BUTTON.clear_border()
        SwitchButton.CUR_BUTTON = self
        self.set_border()
        MainBox.switch_auth(self.depend_form)

    def set_border(self):
        self.setStyleSheet('border: 4px solid #c77d56;')

    def clear_border(self):
        self.setStyleSheet('border: None;')


class ConfirmButton(PushButton):
    INSTANCES: list = []
    BOUND_FUNC = None

    def __init__(self, size: tuple, depend_form, *args):
        super().__init__(size, *args)
        self.depend_form = depend_form
        ConfirmButton.INSTANCES.append(self)
        if self.depend_form == 'GuestBox':   ### TEMP COND
            self.clicked.connect(self.confirm_event)

    @classmethod
    def confirm_event(cls):
        if all(MainBox.CUR_FORM.validate_form()):
            cls.BOUND_FUNC(MainBox.CUR_FORM.login_input.text())
        else:
            MainBox.CUR_FORM.WARNING_INSTANCE.throw_warn()


class HintLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)


class WarningLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)
        self.setStyleSheet('color: red')

    def throw_warn(self):
        self.setText('min 3 letters, max 15 symbols')

