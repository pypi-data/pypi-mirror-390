from bluer_ugv.README.ugvs.comparison.features import UGV_Size, UGV_Cost, UGV_Control
from bluer_ugv.README.ugvs.comparison.ugvs import List_of_UGVs

list_of_ugvs = List_of_UGVs()


list_of_ugvs.add(
    name="ربات موشک‌انداز نذیر",
    control=UGV_Control.RC,
    size=UGV_Size.MEDIUM,
    payload=700,
    range=4,
    cost=UGV_Cost.MEDIUM,
    DYI=False,
)
