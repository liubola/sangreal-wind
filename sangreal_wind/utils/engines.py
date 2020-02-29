"""
数据引擎
"""

import os

import yaml
from sangreal_db import DataBase
from sqlalchemy import create_engine

"""""" """""" """""" """""" """""" ""
"        读取配置文件内容         "
"""""" """""" """""" """""" """""" ""
CONFIG_FILE_NAME = "wind.yaml"
HOME_PATH = os.path.expanduser(f'~{os.sep}.sangreal{os.sep}wind')
if not os.path.exists(HOME_PATH):
    os.makedirs(HOME_PATH)
CONFIG_FILE = os.path.join(HOME_PATH, CONFIG_FILE_NAME)

YAML_TYPE = f"""
wind.config:
    engine: engine url
    schema: blank or other

bundle.config:
    dir: blank or other
"""

if not os.path.isfile(CONFIG_FILE):
#     print(f"{CONFIG_FILE_NAME} does not exist!, you can check {HOME_PATH} and touch it!\
#  The yaml' type is like {YAML_TYPE}")
    config = None
else:
    # 读取数据
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)


def get_db(config, k):
    if config is not None:
        db_config = config.get(k, None)
        if db_config is None:
            raise ValueError(f"Please check the {CONFIG_FILE} and add {k}!\
    The yaml' type is like {YAML_TYPE}")
        engine = create_engine(db_config['engine'])
        schema = db_config['schema']
        return DataBase(engine, schema), engine
    else:
        return DataBase(None), None


def get_bundle(config, k):
    if config is not None:
        bundle_config = config.get(k, None)
        if bundle_config is not None:
            #         raise ValueError(f"Please check the {CONFIG_FILE} and add {k}!\
            # The yaml' type is like {YAML_TYPE}")
            bundle_dir = bundle_config['dir']
            if bundle_dir is None:
                bundle_dir = f"{os.path.expanduser(f'~{os.sep}.sangreal{os.sep}backtest{os.sep}bundle{os.sep}')}"
            return bundle_dir
        else:
            bundle_dir = f"{os.path.expanduser(f'~{os.sep}.sangreal{os.sep}backtest{os.sep}bundle{os.sep}')}"
            return bundle_dir
    else:
        return


# 实例化数据库 ENGINE
WIND_DB, ENGINE = get_db(config, 'wind.config')

# 回测框架本地文件存放的数据
BUNDLE_DIR = get_bundle(config, 'bundle.config')
if BUNDLE_DIR is not None:
    if not BUNDLE_DIR.endswith(os.sep):
        raise ValueError(f'bundle_dir的路径必须以{os.sep}结尾')
    if not os.path.exists(BUNDLE_DIR):
        os.makedirs(BUNDLE_DIR)
