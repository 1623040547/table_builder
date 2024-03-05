import random


class MyUtil:
    colors = []
    cells = {}

    @classmethod
    def gen_colors(cls, length):
        if len(cls.colors) < length:
            for i in range(length):
                color = "#" + "".join([random.choice("ABCDEF") for _ in range(6)])
                cls.colors.append(color)
        return cls.colors[0:length]

    @classmethod
    def pull_list_style(cls, pull_list: [str]):
        """
        下拉列表样式
        :return: Map
        """
        if len(pull_list) == 0:
            return ""
        return {
            "type": "multipleValue",
            "values": pull_list
        }

    @classmethod
    def record_unit_cell(cls, param: str, row: int, column: int, file_id: str, sheet_id: str):
        cls.cells[param] = [row, column, file_id, sheet_id]

    @classmethod
    def link_style(cls, param: str):
        if not cls.cells.__contains__(param):
            return param
        loc = cls.cells[param]
        column = cls.link_column(loc[1])
        row = cls.link_row(loc[0])
        link = 'https://lightweight.feishu.cn/sheets/{0}?sheet={1}&range={2}'.format(
            loc[2],
            loc[3],
            column + row
        )

        return {
            'text': param,
            'link': link,
            'type': 'url'
        }

    @classmethod
    def link_column(cls, index: int):
        """
        :param index: 飞书电子表格列向量下标
        :return: 电子表格单元格列向量'A'-'Z'编码
        """
        ai = index // 4
        bi = index % 4
        a = ord('Q')
        b = ['T', 'j', 'z', 'D']
        return chr(a + ai) + b[bi]

    @classmethod
    def link_row(cls, index: int):
        """
        :param index: 飞书电子表格行向量下标
        :return: 电子表格单元格行向量'0'-'9999'编码
        """
        # 没有找到通解，硬编码0 - 9999
        levels = {
            0: {'1': 'E', '2': 'I', '3': 'M', '4': 'Q', '5': 'U', '6': 'Y', '7': 'Tc', '8': 'Tg', '9': 'Tk'},
            1: {'0': 'w', '1': 'x', '2': 'y', '3': 'z', '4': '0', '5': '1', '6': '2', '7': '3', '8': '4', '9': '5'},
            2: {'0': 'MA', '1': 'MQ', '2': 'Mg', '3': 'Mw', '4': 'NA', '5': 'NQ', '6': 'Ng', '7': 'Nw', '8': 'OA',
                '9': 'OQ'},
            3: {
                '0': 'A', '1': 'E', '2': 'I', '3': 'M', '4': 'Q', '5': 'U', '6': 'Y', '7': 'c', '8': 'g', '9': 'k',
                '00': 'MD', '10': 'MT', '20': 'Mj', '30': 'Mz', '40': 'ND', '50': 'NT', '60': 'Nj', '70': 'Nz',
                '80': 'OD', '90': 'OT'
            },
        }
        # 计算位数
        level = 0
        # 存储位数
        aa = [index % 10]
        # 初始化
        a = index // 10
        while a != 0:
            level += 1
            aa.append(a % 10)
            a = a // 10

        # 和数字相同排序
        aa.reverse()

        def level_0():
            return levels[0][str(aa[0])]

        def level_1():
            return str(level_0()[-1]) + levels[1][str(aa[1])]

        def level_2():
            return level_1() + levels[2][str(aa[2])]

        def level_3():
            return level_1() + levels[3][str(aa[2]) + '0'] + levels[3][str(aa[2])]

        if level == 0:
            return level_0()

        if level == 1:
            return level_1()

        if level == 2:
            return level_2()

        if level == 3:
            return level_3()

        if level == 4:
            return level_3() + levels[2][str(aa[-1])]
