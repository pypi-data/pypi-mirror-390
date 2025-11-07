import argparse
import os
import sys

import yaml
from dotenv import load_dotenv
from jinja2 import Environment, BaseLoader


def get_arguments():
    if any(arg.startswith('test_') or 'pytest' in arg for arg in sys.argv):  # Это тест
        args = None
        cfg_file = './config_pytest.yml'
        if not os.path.exists(cfg_file):
            cfg_file = f".{cfg_file}"
    else:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('-env', choices=['PROD', 'PREPROD', 'UAT', 'TEST', 'DEV', 'LOCAL', 'ENV'],
                                default='DEV', help='Среда в наименовании config')
        arg_parser.add_argument('-name', default='', help='Дополнительный префикс в наименовании config')
        arg_parser.add_argument('-connection_launchers', nargs='*', type=str,
                                help='Список соединений для запуска')
        arg_parser.add_argument('-workers', nargs='*', type=str, help='Список воркеров')
        args = arg_parser.parse_args(sys.argv[1:])
        args_name = f'_{args.name}' if args.name else ''
        cfg_file = f'./config_{args.env}{args_name}.yml'
    return cfg_file, args


class YmlConfig:
    def __init__(self, cfg_name_file='./config.yml', args=None):
        self.args = args
        load_dotenv()
        with open(os.environ.get('ENGINE_CONFIG') or cfg_name_file, encoding='utf8') as f:
            config_yml = f.read()
            if '${' in config_yml:
                config_yml = Environment(
                    loader=BaseLoader(),
                    variable_start_string='${',
                    variable_end_string='}'
                ).from_string(config_yml).render(**dict(os.environ))
            # print('-' * 30)
            # print(config_yml)
            # print('-' * 30)
            self.config = yaml.safe_load(config_yml)

    def __getattr__(self, name: str):
        return self.config.get(name.lower())
