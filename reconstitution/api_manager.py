import json
import random

import requests

from data_model.sheet import SpreadSheets
from util import MyUtil


class ApiManager:
    colors = []

    def __init__(self, sheet: str, table_id: str, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.sheet = sheet
        self.token = self.__get_token()
        self.table_id = table_id
        self.headers = {"Authorization": "Bearer {0}".format(self.token)}
        self.sheets = self.__get_sheets()

    # 获取应用token
    def __get_token(self):
        response = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            data={
                "app_id": self.app_id,
                "app_secret": self.app_secret,
            }
        )
        token = json.loads(bytes.decode(response.content))["tenant_access_token"]
        return token

    # 获取sheets列表
    def __get_sheets(self) -> SpreadSheets:
        response = requests.get(
            "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{0}/sheets/query".format(self.table_id),
            headers=self.headers,
        )
        raw_json = json.loads(bytes.decode(response.content))["data"]
        for sheet in raw_json['sheets']:
            if not sheet.__contains__("merges"):
                sheet["merges"] = []
        return SpreadSheets.from_json(json.dumps(raw_json))

    # 添加行
    def add_rows(self, count: int):
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/dimension_range".format(self.table_id),
            headers=self.headers,
            data=json.dumps(
                {
                    "dimension": {
                        "sheetId": self.sheets.where(self.sheet).sheet_id,
                        "majorDimension": "ROWS",
                        "length": count + 1
                    }
                }
            )
        )
        print(response.content)

    # 移除行
    def remove_rows(self, count: int):
        if count == 1:
            return
        response = requests.delete(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/dimension_range".format(self.table_id),
            headers=self.headers,
            data=json.dumps(
                {
                    "dimension": {
                        "sheetId": self.sheets.where(self.sheet).sheet_id,
                        "majorDimension": "ROWS",
                        "startIndex": 1,
                        "endIndex": count - 1
                    }
                }
            )
        )
        print(response.content)

    # 添加表单
    def add_sheet(self, title: str):
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/sheets_batch_update".format(self.table_id),
            headers=self.headers,
            data=json.dumps({
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": title,
                                "index": 1
                            }
                        }
                    },
                ]
            })
        )
        self.sheets = self.__get_sheets()
        print(response.content)

    # 移除表单样式
    def clean_sheet_style(self, sheet_id: str):
        response = requests.put(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/styles_batch_update".format(self.table_id),
            headers=self.headers,
            data=json.dumps({
                "data": {
                    "ranges": [
                        sheet_id
                    ],
                    "style":
                        {
                            "clean": True
                        },

                }
            })

        )
        print(response.content)

    # 写入值
    def write_values(self, values, alpha: str, number: int):
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(alpha, number),
            chr(ord(alpha) + len(values[0]) - 1) + str(number + len(values) - 1)
        )
        response = requests.put(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/values".format(self.table_id),
            headers=self.headers,
            data=json.dumps(
                {
                    "valueRange": {
                        "range": ran,
                        "values": values
                    }
                })
        )
        print(response.content)

    # 写入背景色
    def write_bg_color(self, width: int, length: int, alpha: str, number: int, color=''):
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(alpha, number),
            chr(ord(alpha) + width - 1) + str(number + length - 1)
        )
        response = requests.put(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/styles_batch_update".format(self.table_id),
            headers=self.headers,
            data=json.dumps(
                {
                    "data": [
                        {
                            "ranges": [ran],
                            "style": {
                                "backColor": color
                            }
                        }
                    ]
                })
        )
        print(response.content)

    # 设置下拉列表
    def set_pull_list(self, values, width: int, length: int, alpha: str, number: int, multi=True, ):
        if length == 0 | len(values) == 0:
            return
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(alpha, number),
            chr(ord(alpha) + width - 1) + str(number + length - 1)
        )
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/dataValidation".format(self.table_id),
            headers=self.headers,
            data=json.dumps(
                {
                    "range": ran,
                    "dataValidationType": "list",
                    "dataValidation": {
                        "conditionValues": values,
                        "options": {
                            "multipleValues": multi,
                            "highlightValidData": True,
                            "colors": MyUtil.gen_colors(len(values))
                        }
                    }
                }
            )
        )
        print(response.content)

    # 合并列
    def merge_column(self, length: int, alpha: str, number: int, ):
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(alpha, number),
            alpha + str(number + length - 1)
        )
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/merge_cells".format(self.table_id),
            headers=self.headers,
            data=json.dumps(
                {
                    "range": ran,
                    "mergeType": "MERGE_COLUMNS",
                }
            )
        )
        print(response.content)

    @classmethod
    def ram_colors(cls, length):
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
    def link_style(cls, text: str, table_id: str, sheet_id: str, column: int, row: int):
        column = cls.__link_column(column)
        row = cls.__link_row(row)
        link = 'https://lightweight.feishu.cn/sheets/{0}?sheet={1}&range={2}'.format(
            table_id,
            sheet_id,
            column + row
        )

        return {
            'text': text,
            'link': link,
            'type': 'url'
        }

    @classmethod
    def __link_column(cls, index: int):
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
    def __link_row(cls, index: int):
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
