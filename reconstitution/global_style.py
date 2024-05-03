from dataclasses import dataclass

from reconstitution.api_manager import ApiManager
from reconstitution.unit_sort import SheetUnitSort


@dataclass
class SheetCrossColor:
    offset_x: int
    offset_y: int
    width: int
    height: int
    color: str


@dataclass
class SheetGlobalStyle:
    cross_colors: list[SheetCrossColor]
    sort: SheetUnitSort


class GlobalStyle:

    def __init__(self, sorts: list[SheetUnitSort]):
        self.sorts = sorts
        self.global_style = []
        for sort in sorts:
            self.global_style.append(
                SheetGlobalStyle(
                    cross_colors=[],
                    sort=sort
                )
            )
        self.set_unit_cross_color()
        self.set_global_cross_color()

    def set_unit_cross_color(self):
        for global_style in self.global_style:
            sort = global_style.sort
            width = len(sort.layout.heads_name)
            offset_x = 0
            offset_y = 1
            ram = 0
            for mark in sort.unit_mark:
                if mark != 0:
                    ram = (ram + 1) % 2
                    height = mark
                    global_style.cross_colors.append(
                        SheetCrossColor(
                            offset_x=offset_x,
                            offset_y=offset_y,
                            width=width,
                            height=height,
                            color=ApiManager.ram_color(ram)
                        )
                    )
                offset_y += 1

    def set_global_cross_color(self):
        for global_style in self.global_style:
            sort = global_style.sort
            ram = 2
            for combine in sort.sheet_combines:
                if combine.is_global:
                    ram += 1
                    global_style.cross_colors.append(
                        SheetCrossColor(
                            offset_x=combine.offset_x,
                            offset_y=combine.offset_y,
                            width=combine.width,
                            height=combine.height,
                            color=ApiManager.ram_color(ram)
                        )
                    )
