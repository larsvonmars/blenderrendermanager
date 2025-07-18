import configparser

CONFIG_FILE = 'settings.ini'


def load_blender_executable():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'Blender' in config and 'ExecutablePath' in config['Blender']:
        return config['Blender']['ExecutablePath']
    return ''


def save_blender_executable(path: str):
    config = configparser.ConfigParser()
    config['Blender'] = {'ExecutablePath': path}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
