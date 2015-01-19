from .cardio_interval import CardioInterval


class CardioSession(object):

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
