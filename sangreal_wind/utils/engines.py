"""
数据引擎
"""

import os
import yaml
from sqlalchemy import create_engine
from sangreal_db import DataBase
"""""" """""" """""" """""" """""" ""
"        读取配置文件内容         "
"""""" """""" """""" """""" """""" ""
CONFIG_FILE_NAME = "wind.yaml"
HOME_PATH = os.path.expanduser(f'~{os.sep}.sangreal{os.sep}wind')
config_file = os.path.join(HOME_PATH, CONFIG_FILE_NAME)

YAML_TYPE = f"""
wind.config:
    engine: engine url
    schema: blank or other
"""

if not os.path.isfile(config_file):
    raise Exception(
        f"{CONFIG_FILE_NAME} does not exist!, check {HOME_PATH} and touch it!\
The yaml' type is like {YAML_TYPE}")

# 读取数据
with open(config_file, 'r') as f:
    config = yaml.load(f)


def get_db(config, k):
    db_config = config.get(k, None)
    if db_config is None:
        raise ValueError(f"Please check the {config_file} and add {k}!")
    engine = create_engine(db_config['engine'])
    schema = db_config['schema']
    return DataBase(engine, schema), engine


WIND_DB, ENGINE = get_db(config, 'wind.config')
