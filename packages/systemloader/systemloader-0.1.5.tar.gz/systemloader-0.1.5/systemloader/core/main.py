from system.module.logger import getlogger
from system.module.ymlconfig import YmlConfig, get_arguments
from system.Daemon import Daemon

if __name__ == '__main__':
    config = YmlConfig(*get_arguments())
    logger = getlogger(f'{config.app_name}_main', config.logger)
    Daemon(config, logger).run()
