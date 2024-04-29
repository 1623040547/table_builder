from dataclasses import dataclass

from reconstitution.api_manager import ApiManager
from reconstitution.config_reader import TableLoad


@dataclass
class SheetUnitLayout:
    load: TableLoad
    sheet_name: str
    sheet_id: str
    heads: list[str]
    heads_redirect: dict
    heads_name: list[str]
    sheet_json: dict
    matrix: list

    def head_index(self, head: str):
        if self.heads.__contains__(head):
            head_i = self.heads.index(head)
            redirect_i = head_i
            for k in self.heads_redirect.keys():
                j = self.heads.index(k)
                if head_i > j:
                    redirect_i = redirect_i + len(self.heads_redirect[k]) - 1
            return redirect_i
        else:
            for k, v in self.heads_redirect.items():
                if v.__contains__(head):
                    head_i = self.head_index(k)
                    return head_i + v.index(head)


class UnitLayout:
    def __init__(self, load: TableLoad):
        self.load = load
        self.index = load.index_json
        self.data = load.data_json

        # 确定表头
        self.heads = []
        self.heads_redirect = {}
        self.heads_name = []
        self.get_heads()

        # 开始布局
        self.layouts: list[SheetUnitLayout] = []
        # 表单划分
        self.split_sheets()
        # 数据矩阵
        self.sheet_to_matrix()

    def get_heads(self):
        for k, v in self.index['data_head'].items():
            if type(v) is str:
                self.heads.append(k)
                self.heads_name.append(v)
            elif type(v) is dict:
                heads_redirect = []
                for k1, v1 in v.items():
                    heads_redirect.append(k1)
                    self.heads_name.append(v1)
                self.heads.append(k)
                self.heads_redirect = {k: heads_redirect}
            else:
                raise

    def split_sheets(self):
        api_manager = ApiManager(
            sheet=self.index['sheet_name'],
            table_id=self.load.table_id,
            app_id=self.load.app_id,
            app_secret=self.load.app_secret
        )
        if self.data.__contains__('data'):
            self.layouts.append(
                SheetUnitLayout(
                    load=self.load,
                    heads=self.heads,
                    heads_redirect=self.heads_redirect,
                    heads_name=self.heads_name,
                    sheet_json=self.data['data'],
                    sheet_name=self.index['sheet_name'],
                    matrix=[],
                    sheet_id=api_manager.create_sheet_id(self.index['sheet_name'])
                )
            )
        elif type(self.data) is list:
            for d in self.data:
                self.layouts.append(
                    SheetUnitLayout(
                        load=self.load,
                        heads=self.heads,
                        heads_redirect=self.heads_redirect,
                        heads_name=self.heads_name,
                        sheet_json=d['data'],
                        sheet_name=d[self.index['sheet_name']],
                        matrix=[],
                        sheet_id=api_manager.create_sheet_id(self.index['sheet_name'])
                    )
                )
        else:
            raise

    def sheet_to_matrix(self):
        for layout in self.layouts:
            layout.matrix.append(layout.heads_name)
            column = len(self.heads_name)
            for unit in layout.sheet_json:
                row = 1
                for k, v in unit.items():
                    if layout.heads_redirect.keys().__contains__(k):
                        row = max(len(v), row)
                # 矩阵初始化
                mat = []
                for i in range(row):
                    ii = []
                    for j in range(column):
                        ii.append('')
                    mat.append(ii)

                for k, v in unit.items():
                    if self.heads_redirect.keys().__contains__(k):
                        row = 0
                        for list_v in v:
                            for key_v, value_v in list_v.items():
                                mat[row][layout.head_index(key_v)] = value_v
                            row += 1
                    else:
                        mat[0][layout.head_index(k)] = v
                layout.matrix.append(mat)
