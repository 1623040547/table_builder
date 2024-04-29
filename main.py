from reconstitution.config_reader import test_config_reader, ConfigReader
from reconstitution.unit_layout import UnitLayout
from reconstitution.unit_sort import UnitSort, SheetUnitSort
from reconstitution.unit_style import UnitStyle

# test_config_reader()

ConfigReader.read_config()

sorts: list[SheetUnitSort] = []
for load in ConfigReader.loads:
    layout = UnitLayout(load)
    print(layout.heads)
    for lay in layout.layouts:
        sort = UnitSort(lay)
        sorts.append(sort.sheet_sort)

UnitStyle(sorts=sorts)

print('suc')
