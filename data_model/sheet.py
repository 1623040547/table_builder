from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json


# 表单名称
class SheetTable(Enum):
    event = "event"
    param = "param"
    union_param = "union_param"


"""
下列数据类参考飞书文档:
https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/query
"""


@dataclass_json
@dataclass
class SheetMerges:
    start_row_index: int
    end_row_index: int
    start_column_index: int
    end_column_index: int


@dataclass_json
@dataclass
class GridProperties:
    frozen_row_count: int
    frozen_column_count: int
    row_count: int
    column_count: int


@dataclass_json
@dataclass
class Sheet:
    index: int
    sheet_id: str
    title: str
    hidden: bool
    resource_type: str
    merges: list[SheetMerges]
    grid_properties: GridProperties


@dataclass_json
@dataclass
class SpreadSheets:
    sheets: list[Sheet]

    def where(self, title) -> Sheet:
        for sheet in self.sheets:
            if sheet.title == title:
                return sheet
        raise

    def where_id(self, sheet_id) -> Sheet:
        for sheet in self.sheets:
            if sheet.sheet_id == sheet_id:
                return sheet
        raise

    def remove(self, title):
        self.sheets.remove(self.where(title))

    def exist(self, title):
        try:
            self.where(title)
            return True
        except:
            return False
