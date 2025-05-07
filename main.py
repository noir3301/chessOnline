import sys
from PyQt6.QtWidgets import *
from PyQt6.QtTest import QTest
from scenes.authorization import AuthScene
from scenes.menu import MenuScene
from scenes.room import RoomScene
from scenes.game import GameScene
from communication.global_data import ConfigData


class MainWindow(QMainWindow):
    def __init__(self, sys_argv, *args):
        super().__init__(*args)
        x_px, y_px = ConfigData().main_win_size
        self.setGeometry(0, 0, x_px, y_px)
        self.auth_scene = AuthScene()
        self.menu_scene = MenuScene()
        self.room_scene = RoomScene()
        self.game_scene = GameScene()
        self.setCentralWidget(self.auth_scene.ui)
        if 'debug' in sys_argv:
            from utils import random_word
            self.auth_scene.auth_confirm(random_word(10))
            if 'host' in sys_argv:
                self.menu_scene.confirm_event('IP','create', 'localhost:65442')
            elif 'client' in sys_argv:
                self.menu_scene.confirm_event('IP', 'join', 'localhost:65442')
            QTest.qWait(3200)
            self.room_scene.game_start('white')
        self.show()

    def set_menu_scene(self):
        self.menu_scene.login_update()
        self.setCentralWidget(self.menu_scene.ui)

    def set_room_scene(self):
        self.room_scene.self_connect()
        self.setCentralWidget(self.room_scene.ui)

    def set_game_scene(self):
        self.game_scene.ui.view.graph_scene.build_figures()
        self.game_scene.ui.view.graph_scene.build_transform_pad()
        self.setCentralWidget(self.game_scene.ui)
        self.game_scene.ui.set_nicknames()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(sys.argv)
    with open('global_styles.qss', 'r') as f:
        _style = f.read()
        app.setStyleSheet(_style)
    app.exec()
    #input("press close to exit")