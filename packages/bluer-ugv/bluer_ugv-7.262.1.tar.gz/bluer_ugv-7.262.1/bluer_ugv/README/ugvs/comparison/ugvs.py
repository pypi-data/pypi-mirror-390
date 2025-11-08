from typing import List
import copy

from bluer_ugv.README.ugvs.comparison.features import (
    list_of_features,
    UGV_Control,
    UGV_Cost,
    UGV_Size,
)


class UGV:
    def __init__(
        self,
        name: str,
        control: UGV_Control,
        size: UGV_Size,
        payload: float,  # kg
        range: float,  # km
        cost: UGV_Cost,
        DYI: bool,
    ):
        self.name = name
        self.control = control
        self.size = size
        self.payload = payload
        self.range = range
        self.cost = cost
        self.DYI = DYI

        self.features = copy.deepcopy(list_of_features)


class List_of_UGVs:
    def __init__(self):
        self.db: List[UGV] = []

    def add(
        self,
        **kw_args,
    ):
        ugv = UGV(**kw_args)
        self.db.append(ugv)
