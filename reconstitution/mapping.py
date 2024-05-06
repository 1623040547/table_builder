from reconstitution.api_manager import ApiManager
from reconstitution.config_reader import ConfigReader
from reconstitution.global_style import SheetGlobalStyle


# 映射顺序:下拉列表、单元格合并、取值、颜色
class SheetMapping:

    def __init__(self, styles: list[SheetGlobalStyle]):
        self.styles = styles
        self.init_sheets()
        self.mapping_pull_list()
        self.mapping_combine()
        self.mapping_values()
        self.mapping_color()

    def init_sheets(self):
        for style in self.styles:
            sort = style.sort
            if self.increment_pass(sort.layout.sheet_id) and sort.layout.sheet_name != 'latest':
                print('increment pass '+ sort.layout.sheet_name)
                continue
            apiManager = ApiManager(
                app_id=sort.layout.load.app_id,
                table_id=sort.layout.load.table_id,
                app_secret=sort.layout.load.app_secret
            )
            # 重置一个表单
            apiManager.clean_sheet_style(sort.layout.sheet_id)
            apiManager.remove_all_rows(sheet_id=sort.layout.sheet_id)
            apiManager.add_rows(
                count=len(sort.layout.matrix),
                sheet_id=sort.layout.sheet_id
            )

    def mapping_pull_list(self):
        for style in self.styles:
            sort = style.sort
            if self.increment_pass(sort.layout.sheet_id) and sort.layout.sheet_name != 'latest':
                continue
            apiManager = ApiManager(
                app_id=sort.layout.load.app_id,
                table_id=sort.layout.load.table_id,
                app_secret=sort.layout.load.app_secret
            )
            for pull in sort.sheet_pulls:
                apiManager.set_pull_list(
                    values=pull.values,
                    width=pull.width,
                    height=pull.height,
                    offset_x=pull.offset_x,
                    offset_y=pull.offset_y,
                    multi=pull.is_multi,
                    sheet_id=sort.layout.sheet_id
                )

    def mapping_values(self):
        for style in self.styles:
            sort = style.sort
            if self.increment_pass(sort.layout.sheet_id) and sort.layout.sheet_name != 'latest':
                continue
            apiManager = ApiManager(
                app_id=sort.layout.load.app_id,
                table_id=sort.layout.load.table_id,
                app_secret=sort.layout.load.app_secret
            )
            value_len = len(sort.layout.matrix)
            offset = 0
            while offset < value_len:
                apiManager.write_values(
                    values=sort.layout.matrix[offset: min(value_len, offset + 100)],
                    offset_x=0,
                    offset_y=offset,
                    sheet_id=sort.layout.sheet_id,
                )
                offset += 100

    def mapping_combine(self):
        for style in self.styles:
            sort = style.sort
            if self.increment_pass(sort.layout.sheet_id):
                continue
            apiManager = ApiManager(
                app_id=sort.layout.load.app_id,
                table_id=sort.layout.load.table_id,
                app_secret=sort.layout.load.app_secret
            )
            for combine in sort.sheet_combines:
                if combine.is_global:
                    apiManager.merge_column(
                        length=combine.height,
                        offset_x=combine.offset_x,
                        offset_y=combine.offset_y,
                        sheet_id=sort.layout.sheet_id
                    )

    def mapping_color(self):
        for style in self.styles:
            sort = style.sort
            if self.increment_pass(sort.layout.sheet_id) and sort.layout.sheet_name != 'latest':
                continue
            apiManager = ApiManager(
                app_id=sort.layout.load.app_id,
                table_id=sort.layout.load.table_id,
                app_secret=sort.layout.load.app_secret,
            )
            offset = 0
            value_len = len(style.cross_colors)
            while offset < value_len:
                colors = []
                for color_style in style.cross_colors[offset:min(value_len, offset + 100)]:
                    colors.append(ApiManager.color_style(
                        width=color_style.width,
                        length=color_style.height,
                        offset_y=color_style.offset_y,
                        offset_x=color_style.offset_x,
                        color=color_style.color,
                        sheet_id=sort.layout.sheet_id
                    ))
                apiManager.write_bg_colors(color_list=colors)
                offset += 100

    # 增量跳过
    def increment_pass(self, sheet_id: str):
        for sheet in ApiManager.new_sheets:
            if sheet.sheet_id == sheet_id:
                return False
        return ConfigReader.is_increment
