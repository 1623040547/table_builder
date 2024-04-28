from dataclasses import dataclass
import json
from dataclasses_json import dataclass_json
import sys
import os


class ConfigReader:
    project_dir = os.path.dirname(sys.argv[0])
    app_id = None
    app_secret = None
    sheet_id = []
    sheet_data = {}

    config = None

    @classmethod
    def read_config(cls):
        config_path = './config.json'
        j = json.load(open(config_path))
        cls.app_id = j["app_id"]
        cls.app_secret = j["app_secret"]
        for t in j["table"]:
            sheet_id = t["sheet_id"]
            cls.sheet_id.append(sheet_id)
            cls.sheet_data[sheet_id] = []
            for k, v in t["template"].items():
                cls.sheet_data[sheet_id].append(
                    [json.load(open(k, encoding='utf-8')), json.load(open(v, encoding='utf-8')), k, v])


def test_config_reader():
    ConfigReader.read_config()
    print(ConfigReader.app_id)
    print(ConfigReader.app_secret)
    print(ConfigReader.sheet_id)
    for i in ConfigReader.sheet_id:
        print(ConfigReader.sheet_data[i])
