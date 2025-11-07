from .quantity import Quantity
from catrxneng.utils import *


class Concentration(Quantity):

    @property
    def molm3(self):
        return self.si

    @molm3.setter
    def molm3(self, value):
        self.si = self.to_float(value)

    @property
    def molL(self):
        return self.si / 1000

    @molL.setter
    def molL(self, value):
        self.si = self.to_float(value * 1000)
