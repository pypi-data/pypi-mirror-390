from .quantity import Quantity
from catrxneng.utils import *


class InvWHSV(Quantity):

    def __init__(self, avg_mol_weight=None, **kwargs):
        super().__init__(**kwargs)
        self.avg_mol_weight = avg_mol_weight

    @property
    def molskgcat(self):
        return self.si

    @molskgcat.setter
    def molskgcat(self, value):
        self.si = self.to_float(value)

    @property
    def molhgcat(self):
        return self.si / 3600 * 1000

    @molhgcat.setter
    def molhgcat(self, value):
        self.si = self.to_float(value) * 3600 / 1000

    @property
    def smLhgcat(self):
        return self.si / 3600 / 22.4

    @smLhgcat.setter
    def smLhgcat(self, value):
        self.si = self.to_float(value) * 3600 * 22.4

    @property
    def inv_h(self):
        try:
            return self.si / 1000 * self.avg_mol_weight * 3600
        except TypeError:
            raise AttributeError("WHSV has no avg_mol_weight assigned.")

    @inv_h.setter
    def inv_h(self, value):
        try:
            self.si = value * 1000 / self.avg_mol_weight / 3600
        except TypeError:
            raise AttributeError("WHSV has no avg_mol_weight assigned.")
