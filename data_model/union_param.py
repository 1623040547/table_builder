import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from data_model.sheet import SheetHead, SheetTable
from util import MyUtil


@dataclass_json
@dataclass
class UnionParam:
    param_name: str
    param_type: str
    param_desc: str
    params: list[str]

    # 参数与表单头相互对应
    def head_map(self):
        return {
            SheetHead.param_name.heads_name(): self.param_name,
            SheetHead.param_type.heads_name(): MyUtil.pull_list_style([self.param_type]),
            SheetHead.param_desc.heads_name(): self.param_desc,
            SheetHead.param_check.heads_name(): "",
        }

    @classmethod
    def alpha(cls, head: SheetHead):
        return chr(ord('A') + SheetHead.index(head, SheetTable.union_param))

    def to_sheet(self):
        items = []
        item0 = []
        # 存放第一行
        for name in SheetHead.head_names(SheetTable.union_param):
            if self.head_map().__contains__(name):
                item0.append(self.head_map()[name])
            elif len(self.params) > 0:
                item0.append(MyUtil.link_style(self.params[0]))
            else:
                item0.append("")
        items.append(item0)
        # 存放后续行（多个参数）
        if len(self.params) > 1:
            for param in self.params[1:]:
                item1 = []
                for name in SheetHead.head_names(SheetTable.union_param):
                    if not self.head_map().__contains__(name):
                        item1.append(MyUtil.link_style(param))
                    else:
                        item1.append("")
                items.append(item1)
        return items

    def number_len(self):
        return max(1, len(self.params))


class UnionParamUtil:
    def __init__(self) -> None:
        self.path = './data/union_params.json'
        self.params = self.get_params()

    def get_params(self):
        my_json = open(self.path).read()
        params = json.loads(my_json)
        tmp = []
        for param in params:
            tmp.append(UnionParam.from_json(json.dumps(param)))
        self.params = tmp
        return tmp

    def param_types(self):
        return [param.param_type for param in self.params]

    def max_number_len(self):
        return len(self.params)
