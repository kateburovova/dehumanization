import os
import json


def init_config(config_path):
    if not os.path.exists(config_path):
        raise Exception("Config file doesn't exist\n"
                        f"Please, create a new config file here {config_path}")

    else:
        with open(config_path) as json_file:
            config = json.load(json_file)

    default_data_folder = "../data"
    if config["channel_data_folder"].startswith(default_data_folder) and not os.path.exists(default_data_folder):
        os.mkdir(default_data_folder)

    if not os.path.exists(config["channel_data_folder"]):
        os.mkdir(config["channel_data_folder"])

    with open(config_path, "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4, ensure_ascii=True)

    return config

