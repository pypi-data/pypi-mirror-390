from catrxneng import utils
from .quantity import Quantity


class EquilibriumConstant(Quantity):
    def __init__(self, order, **kwargs):
        self.order = order
        super().__init__(**kwargs)

    @property
    def Pa(self):
        return self.si

    @Pa.setter
    def Pa(self, value):
        self.si = utils.self.to_float(value)

    @property
    def bar(self):
        return self.si * (100000**self.order)

    @bar.setter
    def bar(self, value):
        self.si = utils.self.to_float(value / (100000**self.order))
