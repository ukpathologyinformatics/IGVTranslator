import yaml

from .dirs import Dirs


class ConfigException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Config(object):
    config_file = Dirs.get_app_path('config.yml')
    igv_port = None
    chain_file = None
    autostart = False

    @staticmethod
    def get_igv_port(if_empty: int = 60151):
        return Config.igv_port if Config.igv_port is not None and Config.igv_port != '' else if_empty

    @staticmethod
    def is_igv_port_valid_for_server():
        return Config.igv_port is not None and Config.igv_port != '' and Config.igv_port != 60151

    @staticmethod
    def set_igv_port(igv_port):
        Config.igv_port = igv_port
        Config.save_config()

    @staticmethod
    def get_chain_file():
        return Config.chain_file

    @staticmethod
    def set_chain_file(chain_file):
        Config.chain_file = chain_file
        Config.save_config()

    @staticmethod
    def get_autostart():
        return Config.autostart

    @staticmethod
    def set_autostart(autostart:bool):
        Config.autostart = autostart
        Config.save_config()

    @staticmethod
    def save_config():
        yaml.safe_dump(
            {
                'igv_port': Config.igv_port,
                'chain_file': Config.chain_file,
                'autostart': Config.autostart,
            },
            open(Config.config_file, 'w'),
            sort_keys=False
        )

    @staticmethod
    def load_config():
        Config.igv_port = None
        Config.chain_file = None
        Config.autostart = False
        try:
            conf = yaml.safe_load(open(Config.config_file, 'r'))
            if conf is None:
                Config.save_config()
                return
            if 'igv_port' in conf:
                Config.igv_port = conf['igv_port']
            if 'chain_file' in conf:
                Config.chain_file = conf['chain_file']
            if 'autostart' in conf:
                Config.autostart = conf['autostart']
        except FileNotFoundError:
            Config.save_config()