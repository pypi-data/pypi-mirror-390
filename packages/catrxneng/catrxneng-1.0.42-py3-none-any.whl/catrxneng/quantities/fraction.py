from .dimensionless import Dimensionless


class Fraction(Dimensionless):

    @property
    def pct(self):
        return self.si * 100

    @pct.setter
    def pct(self, value):
        self.si = value / 100
