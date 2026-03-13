from math import sqrt
from .useful_numbers import Usefulnum, Uncertainty
from .units import Unit

class Physicsnum:
    @staticmethod
    def average(lst):
        sum = 0
        for i in lst:
            sum += i
        avg = sum / len(lst)
        return avg

    @staticmethod
    def standard_error(lst):
        avg = Physicsnum.average(lst)
        sum = 0
        for i in lst:
            sum += (i - avg) ** 2
        vrc = sum / len(lst)
        sde = sqrt(vrc / (len(lst) - 1))
        sde = Usefulnum(sde)
        return sde

    @staticmethod
    def overall_uncertainty(lst, iste):
        sde = Physicsnum.standard_error(lst)
        oau = sqrt(sde.value ** 2 + iste ** 2)
        oau = Uncertainty(oau)
        return oau

    def __init__(self, average: int | float, uncertainty: int | float = 0, unit: str = '1', name: str | None = None, equip_delta: int | float = 0, C=sqrt(3)):
        if type(average) == list:
            self.name = name if type(name) != None else None
            uncertainty = sqrt(uncertainty ** 2 + (equip_delta / C) ** 2)
            self.uncertainty = Physicsnum.overall_uncertainty(average, uncertainty)
            self.average = Usefulnum.same_usefulize(Physicsnum.average(average), self.uncertainty)
        else:
            self.name = name if type(name) != None else None
            self.uncertainty = Uncertainty(sqrt(uncertainty ** 2 + (equip_delta / C) ** 2)) if type(uncertainty) != Uncertainty else uncertainty
            self.average = Usefulnum.same_usefulize(average, self.uncertainty)
        self.unit = Unit(unit) if type(unit) != Unit else unit

    def __str__(self) -> str:
        if self.uncertainty.coef == '0':
            return self.name + ' = ' + str(self.average) + ' ' + str(self.unit) if self.name is not None else str(self.average) + ' ' + str(self.unit)
        if self.name != None:
            if self.average.exponent <= -3 or self.average.exponent >= 3:
                return '{0} = ({1} {2}) x 10^{3} {4}'.format(self.name, self.average.assignexp(self.average.exponent, tuple=True)[0], self.uncertainty.assignexp(self.average.exponent, tuple=True)[0], self.average.exponent, self.unit.str)
            else:
                return '{0} = {1} {2} {3}'.format(self.name, self.average.__str__(), self.uncertainty.__str__(), self.unit.str)
        else:
            if self.average.exponent <= -3 or self.average.exponent >= 3:
                return '({0} {1}) x 10^{2} {3}'.format(self.average.assignexp(self.average.exponent, tuple=True)[0], self.uncertainty.assignexp(self.average.exponent, tuple=True)[0], self.average.exponent, self.unit.str)
            else:
                return '{0} {1} {2}'.format(self.average.__str__(), self.uncertainty.__str__(), self.unit.str)

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, phsnum):
        try:
            phsnum = Physicsnum(phsnum, 0, self.unit) if type(phsnum) != Physicsnum else phsnum
            if self.unit.stable_str != phsnum.unit.stable_str:
                raise Exception('Physicsnum can only be added with the same type of unit')
            newaverage = self.average.value + phsnum.average.value
            newuncertainty = Uncertainty(sqrt(self.uncertainty.value ** 2 + phsnum.uncertainty.value ** 2))
            return Physicsnum(newaverage, newuncertainty, self.unit)
        except Exception as error:
            print('Physicsnum.__add__ function raise errow:', error)

    def __sub__(self, phsnum):
        try:
            phsnum = Physicsnum(phsnum, 0, self.unit) if type(phsnum) != Physicsnum else phsnum
            if self.unit.stable_str != phsnum.unit.stable_str:
                raise Exception('Physicsnum can only be subtricted with the same type of unit')
            newaverage = self.average.value - phsnum.average.value
            newuncertainty = Uncertainty(sqrt(self.uncertainty.value ** 2 + phsnum.uncertainty.value ** 2))
            return Physicsnum(newaverage, newuncertainty, self.unit)
        except Exception as error:
            print('Physicsnum.__add__ function raise errow:', error)

    def __mul__(self, phsnum):
        if type(phsnum) == int or type(phsnum) == float:
            phsnum = Physicsnum(phsnum, 0, '1')
        newaverage = self.average.value * phsnum.average.value
        newuncertainty = Uncertainty(sqrt((phsnum.average.value * self.uncertainty.value) ** 2 + (self.average.value * phsnum.uncertainty.value) ** 2))
        return Physicsnum(newaverage, newuncertainty, self.unit * phsnum.unit)

    def __truediv__(self, phsnum):
        if type(phsnum) == int or type(phsnum) == float:
            phsnum = Physicsnum(phsnum, 0, '1')
        newaverage = self.average.value / phsnum.average.value
        newuncertainty = Uncertainty(sqrt((self.uncertainty.value / phsnum.average.value) ** 2 + (self.average.value * phsnum.uncertainty.value) ** 2 / phsnum.average.value ** 4))
        return Physicsnum(newaverage, newuncertainty, self.unit / phsnum.unit)

    def __pow__(self, num):
        try:
            if type(num) != int:
                raise Exception('Physicsnum can only be powered with int type')
            newaverage = self.average.value ** num
            newuncertainty = Uncertainty(num * self.average.value ** (num - 1) * self.uncertainty.value)
            return Physicsnum(newaverage, newuncertainty, self.unit ** num)
        except Exception as error:
            print('Physicsnum.__pow__ raise error:', error)