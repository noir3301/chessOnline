from scenes.menu.ui import UI, WarningBox, LoginLabel, PasteButton, Slider, ConfirmButton
from multiprocessing import Process, Event as MpEvent
from threading import Thread, Event as TrEvent
from network.irc_client import IRC
from network.client import Client
from network.server import Server
from communication.global_data import NetworkData, PlayerData, ConfigData
from communication.signals import Signals


class Agent:
    def __init__(self):
        NetworkData().serv_stop_event = MpEvent()
        NetworkData().irc_stop_event = TrEvent()
        self.anim_stop_ev = TrEvent()
        PasteButton.DEFAULT_PORT = ConfigData().default_port
        ConfirmButton.BOUND_FUNC = self.confirm_event
        Slider.BOUND_FUNC = self.irc_network
        Signals().work.ip_conn_status.connect(self.ip_conn_status)
        Signals().work.irc_network_status.connect(self.irc_network_status)
        self.slots_dict = {'join': 1, 'create': 0}
        self.ui = UI()

    @staticmethod
    def login_update():
        LoginLabel.login_update(PlayerData().login)

    def confirm_event(self, event_type, *args):
        if event_type == 'IP':
            conn_type, serv_ip_port = args[0], args[1]
            self.ip_room_conn(conn_type, serv_ip_port)
        if event_type == 'IRC':
            try:
                conn_type = args[0]
                room_name = PlayerData().login
                self.irc_room_conn(conn_type, room_name)
            except Exception as e:
                print(e)
        return


    def ip_room_conn(self, conn_type, serv_ip_port):
        NetworkData().serv_ip, NetworkData().serv_port = serv_ip_port.split(':')
        addr = (NetworkData().serv_ip, int(NetworkData().serv_port))
        PlayerData().room_slot = self.slots_dict[conn_type]
        if conn_type == 'create':
            self.run_server(addr)
        self.run_client(addr)

    @staticmethod
    def run_server(addr):
        NetworkData().serv_stop_event.clear()
        NetworkData().serv = Server(addr, 2)
        if NetworkData().serv.exception:
            WarningBox.WARNING_INSTANCE.throw_warn(f'FAILED TO START SERVER ON {addr[0]}:{addr[1]}', 'red')
            ConfirmButton.set_disabled_all(False)
            return
        NetworkData().serv_process = Process(target=NetworkData().serv.listen, daemon=True,
                                             args=(NetworkData().serv_stop_event,))
        NetworkData().serv_process.start()
        WarningBox.WARNING_INSTANCE.throw_warn('CONNECTING...')

    @staticmethod
    def run_client(addr):
        NetworkData().client = Client(addr)
        NetworkData().client_thread = Thread(target=NetworkData().client.connect)
        NetworkData().client_thread.start()

    def ip_conn_status(self, status):
        addr = (NetworkData().serv_ip, int(NetworkData().serv_port))
        if status == 'connected':
            WarningBox.WARNING_INSTANCE.throw_warn(f'CONNECTED TO {addr[0]}:{addr[1]}')
            self.ui.window().set_room_scene()
        elif status == 'failed':
            NetworkData().serv_stop_event.set()
            WarningBox.WARNING_INSTANCE.throw_warn(f'FAILED TO CONNECT TO {addr[0]}:{addr[1]}', 'red')
        else:
            return
        ConfirmButton.set_disabled_all(False)

    def irc_network(self, is_enabled_irc):
        if not is_enabled_irc:
            self.anim_stop_ev.clear()
            anim = Thread(target=self.ui.main_box.top_box.load_box.anim_play, daemon=True, args=(self.anim_stop_ev,))
            anim.start()
            NetworkData().irc_stop_event.clear()
            NetworkData().irc_client = IRC(PlayerData().login, NetworkData().irc_stop_event)
            irc_thread = Thread(target=NetworkData().irc_client.connect)
            irc_thread.start()
        else:
            NetworkData().irc_stop_event.set()
            self.anim_stop_ev.set()
            self.ui.main_box.top_box.slider.set_state('default')
            WarningBox.WARNING_INSTANCE.throw_warn(f'DISCONNECTED FROM THE IRC-NETWORK')

    def irc_network_status(self, status):
        if status == 'connected':
            self.ui.main_box.top_box.slider.set_state('connected')
            WarningBox.WARNING_INSTANCE.throw_warn(f'CONNECTED TO IRC-NETWORK')
        elif status == 'failed':
            self.ui.main_box.top_box.slider.set_state('failed')
            WarningBox.WARNING_INSTANCE.throw_warn(f'FAILED TO CONNECT TO THE IRC-NETWORK', 'red')
        self.anim_stop_ev.set()

    def irc_room_conn(self, conn_type, room_name):
        Signals().work.irc(f'{conn_type}|{room_name}')


    def irc_conn_status(self):
        pass