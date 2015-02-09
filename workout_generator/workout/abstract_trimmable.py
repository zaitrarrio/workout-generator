from abc import ABCMeta
from abc import abstractmethod


class AbstractTrimmable(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_minimum_time_required(self):
        pass

    @abstractmethod
    def get_total_time(self):
        pass

    @property
    def percent_trimmable(self):
        total_time = self.get_total_time()
        if total_time == 0:
            return 0.0
        absolute_trimmable_time = max(float(total_time - self.get_minimum_time_required()), 0.0)
        return absolute_trimmable_time / total_time

    def trim_by_percent(self, percent):
        percent_to_trim = min(self.percent_trimmable, percent)
        return self._trim_by_exact_percent(percent_to_trim)

    @abstractmethod
    def _trim_by_exact_percent(self, percent):
        pass
