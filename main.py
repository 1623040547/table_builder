from reconstitution.config_reader import test_config_reader, ConfigReader
from reconstitution.unit_layout import UnitLayout

# test_config_reader()

ConfigReader.read_config()

for sheet_id, datas in ConfigReader.sheet_data.items():
    for data in datas:
        layout = UnitLayout(data[0], data[1])
        print(layout.head)
