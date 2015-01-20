from workout_generator.utils import get_new_trim_by_percent

from .cardio_interval import CardioInterval
from .abstract_trimmable import AbstractTrimmable

MIN_CARDIO_TIME = 15.0


class CardioSession(AbstractTrimmable):

    def __init__(self, cardio_intervals=None):
        self.cardio_intervals = cardio_intervals or []

    def add_interval(self, cardio_interval):
        self.cardio_intervals.append(cardio_interval)

    def to_json(self):
        # SBL If I want to add more data into the cardio session, just modify
        # this to and from func
        return [ci.to_json() for ci in self.cardio_intervals]

    @classmethod
    def from_json(cls, json_list):
        cardio_intervals = []
        for json_dict in json_list:
            cardio_intervals.append(CardioInterval.from_json(json_dict))
        return cls(cardio_intervals=cardio_intervals)

    def is_empty(self):
        return len(self.cardio_intervals) == 0

    def get_minimum_time_required(self):
        return MIN_CARDIO_TIME

    def get_total_time(self):
        return sum([ci.get_total_time() for ci in self.cardio_intervals])

    def _trim_by_exact_percent(self, percent):
        total_time = self.get_total_time()
        percent = get_new_trim_by_percent(total_time, self.cardio_intervals, percent)
        for cardio_interval in self.cardio_intervals:
            cardio_interval.trim_by_percent(percent)
