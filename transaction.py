from data_model.event import EventUtil, Event
from data_model.event_version import EventVersionUtil
from data_model.param import ParamUtil, Param
from data_model.sheet import SheetHead, SheetTable
from data_model.union_param import UnionParam, UnionParamUtil
from interface import SheetDao
from util import MyUtil
import numpy as np


# 向飞书电子表格写入事件
def write_events():
    # 从本地获取事件数据
    version_util = EventVersionUtil()

    for version, events in version_util.version_events.items():
        dao = SheetDao(sheet=version)

        if dao.sheets.exist(version):
            continue

        dao.add_sheet(version)
        util = EventUtil(events)
        # 写入头
        dao.write_heads(SheetHead.head_names(SheetTable.event))
        dao.add_rows(util.max_number_len() + len(util.plate_events))

        # 写入各事件
        number = 2
        plate_from = number
        plate_index = 0
        for plate in util.plate_events.keys():
            for event in util.plate_events[plate]:
                # 设置起始行
                dao.set_number(number)
                # 操作事件名列
                dao.set_alpha(Event.alpha(SheetHead.event_name))
                dao.merge_column(event.number_len())
                # 操作事件描述列
                dao.set_alpha(Event.alpha(SheetHead.event_desc))
                dao.merge_column(event.number_len())
                # 操作打点平台列
                dao.set_alpha(Event.alpha(SheetHead.panels))
                dao.merge_column(event.number_len())
                dao.set_pull_list(values=util.panels(), multi=True, length=1)
                # 操作触发位置列
                dao.set_alpha(Event.alpha(SheetHead.locations))
                dao.merge_column(event.number_len())
                dao.set_pull_list(values=util.locations(), multi=True, length=1)
                # 操作参数类型列
                dao.set_alpha(Event.alpha(SheetHead.param_type))
                dao.set_pull_list(values=util.param_types(), multi=False, length=len(event.param_list))
                # 写入事件信息
                dao.set_alpha('A')
                dao.write_values(values=event.to_sheet())
                # 写入背景色
                dao.write_bg_color(values=event.to_sheet())
                number += event.number_len()
            # 合并功能模块
            plate_to = number
            dao.set_alpha(Event.alpha(SheetHead.event_plate))
            dao.set_number(plate_from)
            dao.merge_column(plate_to - plate_from)
            dao.write_bg_color(
                np.array([0] * (plate_to - plate_from)).reshape([-1, 1]),
                MyUtil.gen_colors(len(util.plate_events))[plate_index],
            )
            # 重定位
            plate_from = plate_to + 1
            plate_index += 1
            number += 1


# 向飞书电子表格写入参数
def write_params():
    # 从本地获取事件数据
    dao = SheetDao(sheet=SheetTable.param.value)
    dao.clean_sheet(dao.sheets.where(SheetTable.param.value).sheet_id)
    util = ParamUtil()

    # 写入头
    dao.write_heads(SheetHead.head_names(SheetTable.param))
    dao.add_rows(util.max_number_len())

    # 写入各事件
    number = 2
    # 操作参数类型列
    dao.set_alpha(Param.alpha(SheetHead.param_type))
    dao.set_number(2)
    dao.set_pull_list(values=util.param_types(), multi=False, length=len(util.params))
    for count in range(len(util.params) // 10 + 1):
        # 设置起始行
        dao.set_number(number)
        # 写入事件信息
        dao.set_alpha('A')

        part_params = util.params[count * 10:min(count * 10 + 10, len(util.params))]

        values = [param.to_sheet()[0] for param in part_params]

        dao.write_values(values=values)
        # 写入背景色
        dao.write_bg_color(values=values)

        # 记录参数超链接
        for i in range(len(part_params)):
            MyUtil.record_unit_cell(
                param=part_params[i].param_name,
                row=number + i,
                column=0,
                file_id=dao.file_id,
                sheet_id=dao.sheets.where(dao.sheet).sheet_id,
            )

        number += 10


# 向飞书电子表格写入联合参数
def write_union_params():
    # 从本地获取事件数据
    dao = SheetDao(sheet=SheetTable.union_param.value)
    dao.clean_sheet(dao.sheets.where(SheetTable.union_param.value).sheet_id)
    util = UnionParamUtil()

    # 写入头
    dao.write_heads(SheetHead.head_names(SheetTable.union_param))
    dao.add_rows(util.max_number_len())

    # 写入各事件
    number = 2
    for param in util.params:
        # 设置起始行
        dao.set_number(number)
        # 操作参数类型列
        dao.set_alpha(UnionParam.alpha(SheetHead.param_type))
        dao.set_pull_list(values=util.param_types(), multi=False, length=1)
        # 写入事件信息
        dao.set_alpha('A')
        dao.write_values(values=param.to_sheet())
        # 写入背景色
        dao.write_bg_color(values=param.to_sheet())
        # 记录参数超链接
        MyUtil.record_unit_cell(
            param=param.param_name,
            row=number,
            column=0,
            file_id=dao.file_id,
            sheet_id=dao.sheets.where(dao.sheet).sheet_id,
        )
        number += param.number_len()
