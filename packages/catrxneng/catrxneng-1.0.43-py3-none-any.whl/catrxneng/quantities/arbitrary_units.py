from .quantity import Quantity
from catrxneng.utils import *


class ArbitraryUnits(Quantity):

    def __init__(self, value, units, units_pwr):
        self.value = value
        self.units = units
        self.units_pwr = units_pwr
