from typing import Dict, Callable

from enum import Enum


class UGV_Control(Enum):
    RC_AI = 3
    AI = 2
    RC = 1


class UGV_Cost(Enum):
    LOW = 100  # < 50 mT ~= $500
    MEDIUM = 10  # < 500 mT ~= $5k
    HIGHT = 1  # < 5 MT ~= $50k


class UGV_Size(Enum):
    SMALL = 100
    MEDIUM = 10
    LARGE = 1


class Feature:
    def __init__(
        self,
        name,
        score: int = -1,
        better_func: Callable = lambda score_1, score_2: score_1 > score_2,
    ):
        self.name = name
        self.score = score
        self.better_func = better_func


class FeatureList:
    def __init__(self):
        self.db: Dict[Feature] = {}

    def add(self, feature: Feature):
        self.db[feature] = False


list_of_features: FeatureList = FeatureList()

for feature_name in [
    "سامانه‌ی هوش مصنوعی",
    "سامانه‌ی مکان‌یابی",
    "فعالیت گروهی",
    "شعاع عملکرد عملیاتی نامحدود",
    "قابلیت استتار و کمین درازمدت",
    "حمل پهپاد و رهپاد",
    "تحریم گریزی",
]:
    FeatureList.add(Feature(feature_name))
