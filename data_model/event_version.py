import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from data_model.event import Event
from data_model.param import Param
from data_model.sheet import SheetHead, SheetTable
from data_model.union_param import UnionParam
from util import MyUtil


@dataclass_json
@dataclass
class EventVersion:
    data: list[Event]
    version: str


class EventVersionUtil:
    def __init__(self) -> None:
        self.path = './data/events.json'
        self.events = self.get_events()
        self.version_events = {}
        for e in self.events:
            self.version_events[e.version] = e.data

    def get_events(self) -> list[EventVersion]:
        my_json = open(self.path).read()
        events = json.loads(my_json)
        tmp = []
        for event in events:
            tmp.append(EventVersion.from_json(json.dumps(event)))
        self.events = tmp
        return tmp
