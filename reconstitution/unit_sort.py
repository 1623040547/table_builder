from dataclasses import dataclass

from reconstitution.unit_layout import SheetUnitLayout


@dataclass
class SheetCombine:
    offset_x: int
    offset_y: int
    width: int
    height: int


@dataclass
class SheetPullList:
    is_multi: bool
    offset_x: int
    offset_y: int
    width: int
    height: int
    values: [str]


@dataclass
class SheetUnitSort:
    layout: SheetUnitLayout
    sheet_combines: list[SheetCombine]
    sheet_pulls: list[SheetPullList]


@dataclass
class PriorityTreeNode:
    mount_name: str
    value: str
    units: list
    next: None

    def get_leaf_nodes(self):
        if self.next is None:
            return [self]
        leaf_nodes = []
        for nex in list(self.next):
            leaf_nodes.extend(nex.get_leaf_nodes())
        return leaf_nodes


class UnitSort:
    def __init__(self, layout: SheetUnitLayout):
        self.layout = layout
        self.index_json = self.layout.load.index_json
        try:
            self.global_mounts: [str] = self.index_json['global_style']['combine']
        except:
            self.global_mounts: [str] = []
        try:
            self.unit_mounts: [str] = self.index_json['unit_style']['pull_list']
        except:
            self.unit_mounts: [str] = []

        self.priority_tree = PriorityTreeNode(
            mount_name='',
            value='',
            units=self.layout.matrix[1:],
            next=None
        )
        self.global_priority_mount()
        self.unit_priority_mount()
        self.resort_layout()

        self.sheet_sort = SheetUnitSort(
            layout=self.layout,
            sheet_combines=[],
            sheet_pulls=[],
        )
        self.set_combines()
        self.set_pulls()

    def global_priority_mount(self):
        if len(self.global_mounts) == 0:
            return
        for mount in self.global_mounts:
            i = self.layout.head_index(mount)
            for node in self.priority_tree.get_leaf_nodes():
                new_nodes: dict[str:PriorityTreeNode] = {}
                for unit in node.units:
                    value = unit[0][i]
                    if new_nodes.keys().__contains__(value):
                        new_nodes[value].units.append(unit)
                    else:
                        new_nodes[value] = PriorityTreeNode(
                            mount_name=mount,
                            value=value,
                            units=[unit],
                            next=None
                        )
                node.next = new_nodes.values()
                node.units.clear()

    def unit_priority_mount(self):
        if len(self.unit_mounts) == 0:
            return
        for mount in self.unit_mounts:
            for node in self.priority_tree.get_leaf_nodes():
                new_nodes: dict[int:PriorityTreeNode] = {}
                for unit in node.units:
                    row = len(unit)
                    i = self.layout.head_index(mount)
                    pull_unit = unit[0][i]
                    if type(pull_unit) is list and len(pull_unit) == 0:
                        row = 0
                    elif type(pull_unit) is str and pull_unit == '':
                        row = 0
                    if new_nodes.keys().__contains__(row):
                        new_nodes[row].units.append(unit)
                    else:
                        new_nodes[row] = PriorityTreeNode(
                            mount_name='unit_priority_mount',
                            value=str(row),
                            units=[unit],
                            next=None
                        )
                node.next = [new_nodes[i] for i in sorted(new_nodes)]
                node.units.clear()

    def resort_layout(self):
        self.layout.matrix = [self.layout.matrix[0]]
        for node in self.priority_tree.get_leaf_nodes():
            for unit in node.units:
                unit[0].append(len(unit))
                for row in unit[1:]:
                    row.append(0)
                self.layout.matrix.extend(unit)

    # [global_style.combine] [unit_style.combine]
    def set_combines(self):
        try:
            global_combines = self.index_json['global_style']['combine']
        except:
            global_combines = []
        global_map = {}
        try:
            unit_combines = self.index_json['unit_style']['combine']
        except:
            unit_combines = []
        combines: list[SheetCombine] = []
        for i, row in enumerate(self.layout.matrix[1:]):
            i = i + 1
            if row[-1] != 0:
                for unit_combine in unit_combines:
                    if row[-1] == 1:
                        continue
                    combines.append(SheetCombine(
                        offset_x=self.layout.head_index(unit_combine),
                        offset_y=i,
                        width=1,
                        height=row[-1]
                    ), )
                for global_combine in global_combines:
                    index_g = self.layout.head_index(global_combine)
                    if not global_map.__contains__(global_combine):
                        global_map[global_combine] = [row[index_g], i]
                    elif global_map[global_combine][0] != row[index_g]:
                        height = i - global_map[global_combine][1]
                        if height == 1:
                            continue
                        combines.append(SheetCombine(
                            offset_x=index_g,
                            offset_y=global_map[global_combine][1],
                            width=1,
                            height=height
                        ), )
                        global_map[global_combine][1] = i
        self.sheet_sort.sheet_combines = combines

    # [unit_style.pull_list]
    def set_pulls(self):
        try:
            pull_list = self.index_json['unit_style']['pull_list']
        except:
            pull_list = []
        pull_map = {}
        pulls: list[SheetPullList] = []
        for i, row in enumerate(self.layout.matrix[1:]):
            i = i + 1
            for pull_item in pull_list:
                index_p = self.layout.head_index(pull_item)
                if type(row[index_p]) is list and len(row[index_p]) != 0:
                    is_multi = True
                    items = row[index_p]
                elif type(row[index_p]) is str and row[index_p] != '':
                    is_multi = False
                    items = [row[index_p]]
                else:
                    if pull_map.__contains__(pull_item) and pull_map[pull_item][0]:
                        pull_map[pull_item][0] = False
                        pulls.append(SheetPullList(
                            is_multi=pull_map[pull_item][-1],
                            offset_x=index_p,
                            offset_y=pull_map[pull_item][1],
                            width=1,
                            height=i - pull_map[pull_item][1],
                            values=pull_map[pull_item][2]
                        ))
                    continue
                if not pull_map.__contains__(pull_item):
                    pull_map[pull_item] = [True, i, items, is_multi]
                else:
                    if not pull_map[pull_item][0]:
                        pull_map[pull_item][0] = True
                        pull_map[pull_item][1] = i
                    pull_map[pull_item][2].extend(items)
        self.sheet_sort.sheet_pulls = pulls
