from reconstitution.config_reader import test_config_reader, ConfigReader
from reconstitution.unit_layout import UnitLayout

# test_config_reader()

ConfigReader.read_config()

for load in ConfigReader.loads:
    layout = UnitLayout(load)
    print(layout.heads)
