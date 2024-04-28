import requests
import json
from data_model.sheet import SpreadSheets, SheetTable
import random

from util import MyUtil

my_healer_file_id = "A4VhsjDEqhzEpXtbxNhcZGb4nCe"


def get_token():
    response = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data={
            "app_id": "cli_a5321589fbfb900e",
            "app_secret": "npcTpll8Ik4A7bGxoejDyfMMWocfh8g2",
        }
    )
    token = json.loads(bytes.decode(response.content))["tenant_access_token"]
    return token


class SheetDao:
    active_file_id = ''

    def __init__(self, sheet: str) -> None:
        self.sheet = sheet
        self.token = get_token()
        self.file_id = my_healer_file_id
        self.headers = {"Authorization": "Bearer {0}".format(self.token)}
        self.sheets = self.get_sheets()
        self.number = 1
        self.alpha = 'A'
        self.whichColor = True

    def set_number(self, number: int):
        self.number = number

    def set_alpha(self, alpha: str):
        self.alpha = alpha

    def write_heads(self, heads: [str]):  # type: ignore
        self.write_values(values=[heads])

    def add_rows(self, count: int):
        c = self.sheets.where(self.sheet).grid_properties.row_count
        count = count - c + 1
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/dimension_range".format(self.file_id),
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

    def remove_rows(self, count: int):
        if count == 1:
            return
        response = requests.delete(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/dimension_range".format(self.file_id),
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

    def add_sheet(self, title: str):
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/sheets_batch_update".format(self.file_id),
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
        self.sheets = self.get_sheets()
        print(response.content)

    def clean_sheet(self, sheet_id: str):
        response = requests.put(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/styles_batch_update".format(self.file_id),
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
        self.remove_rows(self.sheets.where(self.sheet).grid_properties.row_count)
        self.add_rows(self.sheets.where(self.sheet).grid_properties.row_count * 2)
        print(response.content)

    def get_sheets(self) -> SpreadSheets:
        response = requests.get(
            "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{0}/sheets/query".format(self.file_id),
            headers=self.headers,
        )
        raw_json = json.loads(bytes.decode(response.content))["data"]
        for sheet in raw_json['sheets']:
            if not sheet.__contains__("merges"):
                sheet["merges"] = []
        return SpreadSheets.from_json(json.dumps(raw_json))

    def write_values(self, values):
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(self.alpha, self.number),
            chr(ord(self.alpha) + len(values[0]) - 1) + str(self.number + len(values) - 1)
        )
        response = requests.put(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/values".format(self.file_id),
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

    def write_bg_color(self, values, color=''):
        if color == '':
            if self.whichColor:
                color = "#F6FAFD"
            else:
                color = "#F6F6FA"
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(self.alpha, self.number),
            chr(ord(self.alpha) + len(values[0]) - 1) + str(self.number + len(values) - 1)
        )
        response = requests.put(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/styles_batch_update".format(self.file_id),
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
        self.whichColor = not self.whichColor
        print(response.content)

    def set_pull_list(self, values, length: int, multi=True):
        if length == 0 | len(values) == 0:
            return
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(self.alpha, self.number),
            self.alpha + str(self.number + length - 1)
        )
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/dataValidation".format(self.file_id),
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

    def merge_column(self, length: int,):
        ran = "{0}!{1}:{2}".format(
            self.sheets.where(self.sheet).sheet_id,
            "{0}{1}".format(self.alpha, self.number),
            self.alpha + str(self.number + length - 1)
        )
        response = requests.post(
            "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{0}/merge_cells".format(self.file_id),
            headers=self.headers,
            data=json.dumps(
                {
                    "range": ran,
                    "mergeType": "MERGE_COLUMNS",
                }
            )
        )
        print(response.content)
