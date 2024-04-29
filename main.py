from reconstitution.config_reader import test_config_reader, ConfigReader
from reconstitution.unit_layout import UnitLayout
from reconstitution.unit_sort import UnitSort

# test_config_reader()

ConfigReader.read_config()

sorts = []
for load in ConfigReader.loads:
    layout = UnitLayout(load)
    print(layout.heads)
    for lay in layout.layouts:
        sort = UnitSort(lay)
        sorts.append(sort)

print('suc')