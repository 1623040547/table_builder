import numpy as np


class UnitLayout:
    def __init__(self, index: dict, data: dict):
        self.head = []
        self.sub_head = {}
        self.head_name = []
        self.sheet = {}
        self.index = index
        self.data = data
        self.table_matrix = {}
        self.sheet_head()
        self.sheet_split()
        self.sheet_to_matrix()



    def index0(self, name: str) -> int:
        if self.head.__contains__(name):
            i = self.head.index(name)
            ii = i
            for k in self.sub_head.keys():
                j = self.head.index(k)
                if i > j:
                    ii = ii + len(self.sub_head[k]) - 1
            return ii
        else:
            for k, v in self.sub_head.items():
                if v.__contains__(name):
                    i = self.index0(k)
                    return i + v.index(name)
        raise

    def sheet_head(self):
        for k, v in self.index['data_head'].items():
            if type(v) is str:
                self.head.append(k)
                self.head_name.append(v)
            elif type(v) is dict:
                sub_head = []
                for k1, v1 in v.items():
                    sub_head.append(k1)
                    self.head_name.append(v1)
                self.head.append(k)
                self.sub_head = {k: sub_head}
            else:
                raise

    def sheet_split(self):
        if self.data.__contains__('data'):
            self.sheet[self.index['sheet_name']] = self.data['data']
        elif type(self.data) is list:
            for d in self.data:
                self.sheet[d[self.index['sheet_name']]] = d['data']
        else:
            raise

    def sheet_to_matrix(self):
        for sheet_name, units in self.sheet.items():
            print(sheet_name)
            if sheet_name == '参数':
                print()
                pass
            matrix = []
            matrix.append(self.head_name)
            column = len(self.head_name)
            for unit in units:
                row = 1
                for k, v in unit.items():
                    if k == 'union_param_list':
                        continue
                    if self.sub_head.keys().__contains__(k):
                        row = max(len(v), row)
                mat0 = []
                for i in range(row):
                    ii = []
                    for j in range(column):
                        ii.append('')
                    mat0.append(ii)
                for k, v in unit.items():
                    if k == 'union_param_list':
                        continue
                    if self.sub_head.keys().__contains__(k):
                        row = 0
                        for v_list in v:
                            if type(v_list) is not dict:
                                continue
                            for v_key, v_value in v_list.items():
                                if v_key == 'params':
                                    continue
                                mat0[row][self.index0(v_key)] = v_value
                            row += 1
                    else:
                        index = self.index0(k)
                        mat0[0][index] = v
                matrix.append(mat0)

            self.table_matrix[sheet_name] = matrix
            print(matrix)