from scenes.authorization.ui import UI, ConfirmButton
from communication.global_data import PlayerData

class Agent:
    def __init__(self):
        ConfirmButton.BOUND_FUNC = self.auth_confirm
        self.ui = UI()

    def auth_confirm(self, login):
        PlayerData().login = login
        self.ui.window().set_menu_scene()
