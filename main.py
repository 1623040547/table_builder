from data_model.event import Event, EventUtil
from interface import SheetDao
from transaction import write_events, write_params, write_union_params

import json

write_params()

write_union_params()

write_events()
