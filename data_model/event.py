from dataclasses import dataclass
from dataclasses_json import dataclass_json

from data_model.param import Param
from data_model.sheet import SheetHead, SheetTable
from data_model.union_param import UnionParam
from util import MyUtil


@dataclass_json
@dataclass
class Event:
    event_name: str
    event_desc: str
    event_plate: str
    panels: list[str]
    locations: list[str]
    param_list: list[Param]
    union_param_list: list[UnionParam]

    # 参数与表单头相互对应
    def head_map(self):
        return {
            SheetHead.event_name.head_name(): self.event_name,
            SheetHead.event_desc.head_name(): self.event_desc,
            SheetHead.event_plate.head_name(): self.event_plate,
            SheetHead.locations.head_name(): MyUtil.pull_list_style(self.locations),
            SheetHead.panels.head_name(): MyUtil.pull_list_style(self.panels),
        }

    # 将事件转换为电子表格所能接受的格式
    def to_sheet(self):
        items = []
        item0 = []
        # 存放第一行
        for name in SheetHead.head_names(SheetTable.event):
            if self.head_map().__contains__(name):
                item0.append(self.head_map()[name])
            elif len(self.param_list) > 0:
                tmp = self.param_list[0].head_map()[name]
                if name == SheetHead.param_name.head_name():
                    tmp = MyUtil.link_style(tmp)
                item0.append(tmp)
            else:
                item0.append("")
        items.append(item0)
        # 存放后续行（多个参数）
        if len(self.param_list) > 1:
            for param in self.param_list[1:]:
                item1 = []
                for name in SheetHead.head_names(SheetTable.event):
                    if param.head_map().__contains__(name):
                        tmp = param.head_map()[name]
                        if name == SheetHead.param_name.head_name():
                            tmp = MyUtil.link_style(tmp)
                        item1.append(tmp)
                    else:
                        item1.append("")
                items.append(item1)
        return items

    def number_len(self):
        return max(1, len(self.param_list))

    @classmethod
    def alpha(cls, head: SheetHead):
        return chr(ord('A') + SheetHead.index(head, SheetTable.event))


class EventUtil:
    def __init__(self, events: [Event]) -> None:
        self.path = './data/events.json'
        self.events = events
        self.plate_events = {}
        for e in self.events:
            if not self.plate_events.__contains__(e.event_plate):
                self.plate_events[e.event_plate] = [e]
            else:
                self.plate_events[e.event_plate].append(e)

    def locations(self):
        tmp = []
        for event in self.events:
            tmp.extend(event.locations)
        return list(set(tmp))

    def panels(self):
        tmp = []
        for event in self.events:
            tmp.extend(event.panels)
        return list(set(tmp))

    def param_types(self):
        tmp = []
        for event in self.events:
            for param in event.param_list:
                tmp.append(param.param_type)
            for union_param in event.union_param_list:
                tmp.append(union_param.param_type)
        return list(set(tmp))

    def max_number_len(self):
        count = 0
        for event in self.events:
            count += max(1, len(event.param_list))
        return count
