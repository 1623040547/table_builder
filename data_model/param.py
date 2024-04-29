import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from data_model.sheet import SheetHead, SheetTable
from util import MyUtil


@dataclass_json
@dataclass
class Param:
    param_name: str
    param_type: str
    param_desc: str
    param_check: str

    # 参数与表单头相互对应
    def head_map(self):
        return {
            SheetHead.param_name.heads_name(): self.param_name,
            SheetHead.param_type.heads_name(): MyUtil.pull_list_style([self.param_type]),
            SheetHead.param_desc.heads_name(): self.param_desc,
            SheetHead.param_check.heads_name(): self.param_check,
        }

    @classmethod
    def alpha(cls, head: SheetHead):
        return chr(ord('A') + SheetHead.index(head, SheetTable.param))

    def to_sheet(self):
        items = [[]]
        for name in SheetHead.head_names(SheetTable.param):
            if self.head_map().__contains__(name):
                items[0].append(self.head_map()[name])
            else:
                items[0].append("")
        return items


class ParamUtil:
    def __init__(self) -> None:
        self.path = './data/params.json'
        self.params = self.get_params()

    def get_params(self):
        my_json = open(self.path).read()
        params = json.loads(my_json)
        tmp = []
        for param in params:
            tmp.append(Param.from_json(json.dumps(param)))
        self.params = tmp
        return tmp

    def param_types(self):
        return [param.param_type for param in self.params]

    def max_number_len(self):
        return len(self.params)
