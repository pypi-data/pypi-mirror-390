from .quantity import Quantity


class Moles(Quantity):

    @property
    def mol(self):
        return self.si

    @mol.setter
    def mol(self, value):
        self.si = self.to_float(value)
