from reconstitution.config_reader import ConfigReader
from reconstitution.global_style import GlobalStyle
from reconstitution.mapping import SheetMapping
from reconstitution.unit_layout import UnitLayout
from reconstitution.unit_sort import UnitSort, SheetUnitSort
from reconstitution.unit_style import UnitStyle

# test_config_reader()

# 读取配置
ConfigReader.read_config()
sorts: list[SheetUnitSort] = []
# 数据布局
for load in ConfigReader.loads:
    layout = UnitLayout(load)
    for lay in layout.layouts:
        sort = UnitSort(lay)
        sorts.append(sort.sheet_sort)
# 数据样式
UnitStyle(sorts=sorts)
g = GlobalStyle(sorts=sorts)
# API映射
SheetMapping(styles=g.global_style)
