from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json


# 表单名称
class SheetTable(Enum):
    event = "event"
    param = "param"
    union_param = "union_param"


# 电子表格的所有表列名，目前所有表单列名放在一起，每个表单可能只是分有其中的一些列名
class SheetHead(Enum):
    event_name = ["事件名", {SheetTable.event}]
    event_desc = ["事件描述", {SheetTable.event}]
    param_name = ["参数名", {SheetTable.event, SheetTable.param, SheetTable.union_param}]
    param_desc = ["参数描述", {SheetTable.event, SheetTable.param, SheetTable.union_param}]
    param_type = ["参数数据类型", {SheetTable.event, SheetTable.param, SheetTable.union_param}]
    param_check = ["参数类型检查", {SheetTable.event, SheetTable.param}]
    locations = ["事件触发位置", {SheetTable.event}]
    panels = ["打点平台", {SheetTable.event}]
    event_plate = ["功能模块", {SheetTable.event}]
    sub_params = ["子参数", {SheetTable.union_param}]

    @classmethod
    def head_names(cls, table: SheetTable):
        heads = []
        for h in SheetHead:
            if h.value[1].__contains__(table):
                heads.append(h.head_name())
        return heads

    def head_name(self):
        return self.value[0]

    def index(self, table: SheetTable):
        i = 0
        for h in SheetHead:
            if self.value == h.value:
                return i
            for s in h.value[1]:
                if s == table:
                    i += 1
        raise


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
