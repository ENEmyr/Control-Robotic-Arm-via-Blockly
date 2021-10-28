import configparser
from sys import path as root_path
from os import path

CONFIG = configparser.ConfigParser()
CURRENT_PATH = path.join(root_path[0], 'configs')

class BrokerConfig:
    CONFIG.read_file(open(path.join(CURRENT_PATH, 'config.cfg')))
    Username = CONFIG.get(section='Broker', option='Username')
    Key = CONFIG.get(section='Broker', option='Key')
    Thing = CONFIG.get(section='Broker', option='Thing')

    @staticmethod
    def __setattr__(name, value):
        ''' Overridden __setattr__ method to update configuration file when new attribute got updated'''
        if name in BrokerConfig.__dict__.keys():
            CONFIG.set(section='Broker', option=name, value=value)
            with open(path.join(CURRENT_PATH, 'config.cfg'), 'w') as configfile:
                CONFIG.write(configfile)
            BrokerConfig.Username = CONFIG.get(section='Broker', option='Username')
            BrokerConfig.Key = CONFIG.get(section='Broker', option='Key')
            BrokerConfig.Thing = CONFIG.get(section='Broker', option='Thing')
        else:
            raise Exception('Has no attribute.')
