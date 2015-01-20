from workout_generator.utils import base_round

from .abstract_trimmable import AbstractTrimmable


class CardioInterval(AbstractTrimmable):

    def __init__(self, zone, minutes, min_heart_rate, max_heart_rate):
        self.zone = zone
        self.minutes = minutes
        self.min_heart_rate = min_heart_rate
        self.max_heart_rate = max_heart_rate

    def get_minimum_time_required(self):
        return 1.0

    def get_total_time(self):
        return self.minutes

    def _trim_by_exact_percent(self, percent):
        minutes_to_subtract = self.minutes * percent
        self.minutes -= minutes_to_subtract
        seconds = self.minutes * 60
        seconds = base_round(seconds, base=5)
        self.minutes = float(seconds) / 60

    @classmethod
    def from_cardio_zone(self, cardio_zone):
        return CardioInterval(
            cardio_zone.zone,
            cardio_zone.interval,
            cardio_zone.min_heart_rate,
            cardio_zone.max_heart_rate
        )

    @classmethod
    def from_json(self, json_dict):
        return CardioInterval(
            json_dict["zone"],
            json_dict["minutes"],
            json_dict["min_heart_rate"],
            json_dict["max_heart_rate"]
        )

    def to_json(self):
        return {
            "zone": self.zone,
            "minutes": self.minutes,
            "min_heart_rate": self.min_heart_rate,
            "max_heart_rate": self.max_heart_rate
        }
