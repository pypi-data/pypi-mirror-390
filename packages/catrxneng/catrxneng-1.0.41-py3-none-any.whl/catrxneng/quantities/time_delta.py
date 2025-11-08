from .quantity import Quantity
from catrxneng import utils


class TimeDelta(Quantity):

    @property
    def sec(self):
        return self.si

    @sec.setter
    def sec(self, value):
        self.si = utils.self.to_float(value)

    @property
    def min(self):
        return utils.divide(self.si, 60)

    @min.setter
    def min(self, value):
        self.si = value * 60

    @property
    def hr(self):
        return utils.divide(self.si, 3600)

    @hr.setter
    def hr(self, value):
        self.si = value * 3600
