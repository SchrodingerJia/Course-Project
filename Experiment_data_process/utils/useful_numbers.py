from math import sqrt

class Usefulnum:
    @staticmethod
    def sround(numstr: str, index: int) -> str:
        if index > 0:
            if numstr[index + 2] < '5' or (numstr[index + 2] == '5' and int(numstr[index + 1]) % 2 == 0):
                num = numstr[:index + 2]
            else:
                tmp = str(int(numstr[0] + numstr[2:index + 2]) + 1)
                num = tmp[:-index] + '.' + tmp[-index:]
            return num
        elif index == 0:
            if numstr[2] < '5' or (numstr[2] == '5' and int(numstr[0]) % 2 == 0):
                num = numstr[0]
            else:
                num = str(int(numstr[0]) + 1)
            return num
        else:
            return numstr

    def __init__(self, value: int | float, usefulindex: int = 6):
        try:
            if type(value) == Usefulnum:
                self.coef = value.coef
                self.exponent = value.exponent
                self.usefulindex = value.usefulindex
                self.negetive = value.negetive
                self.finalexp = value.finalexp
                self.initvalue = value.initvalue
                self.value = value.value
            else:
                if type(value) != int and type(value) != float:
                    raise Exception('value\'type must be int or float')
                if type(usefulindex) != int:
                    raise Exception('usefulindex\'type must be int')
                if usefulindex > 6 or usefulindex <= 0:
                    raise Exception('usefulindex should be no more than 6 and no less than 1')
                num = '{0:e}'.format(value)
                coef, exponent = tuple(num.split('e'))
                self.negetive = '-' if coef.startswith('-') else ''
                coef = coef[1:] if coef.startswith('-') else coef
                coef = self.sround(coef, usefulindex - 1)
                if not coef.startswith('10'):
                    self.coef = coef
                    self.exponent = int(exponent)
                elif coef == '10':
                    self.coef = '1'
                    self.exponent = int(exponent) + 1
                else:
                    self.coef = '1.0' + coef[3:-1]
                    self.exponent = int(exponent) + 1
                self.initvalue = value
                self.value = float(self.negetive + coef + 'e' + exponent)
                self.usefulindex = usefulindex
                self.finalexp = int(exponent) - usefulindex + 1
        except Exception as error:
            print('Usefulnum.__init__ function raise errow:', error)

    def __str__(self) -> str:
        if self.exponent == 0:
            rtn = self.coef
        elif self.exponent < 0:
            rtn = '0.' + '0' * (-self.exponent - 1) + self.coef[0] + self.coef[2:]
        elif self.usefulindex == 1:
            rtn = self.coef + '0' * self.exponent
        elif self.usefulindex - 1 > self.exponent:
            rtn = self.coef[0] + self.coef[2:self.exponent + 2] + '.' + self.coef[self.exponent + 2:]
        else:
            rtn = self.coef[0] + self.coef[2:] + '0' * (self.exponent - self.usefulindex + 1)
        return self.negetive + rtn

    def __repr__(self) -> str:
        return self.__str__()

    def assignexp(self, asexp: int | str = 0, tuple=False) -> str | tuple:
        if asexp == 'int':
            asexp = self.exponent - self.usefulindex + 1
        else:
            asexp = int(asexp)
        diffexp = self.exponent - asexp
        if diffexp == 0:
            asstr = self.coef
        elif diffexp < 0:
            asstr = '0.' + '0' * (-diffexp - 1) + self.coef[0] + self.coef[2:]
        elif self.usefulindex == 1:
            asstr = self.coef + '0' * diffexp
        elif self.usefulindex - 1 > diffexp:
            asstr = self.coef[0] + self.coef[2:diffexp + 2] + '.' + self.coef[diffexp + 2:]
        else:
            asstr = self.coef[0] + self.coef[2:] + '0' * (diffexp - self.usefulindex + 1)
        return '{0} x 10^{1}'.format(self.negetive + asstr, asexp) if tuple == False else (self.negetive + asstr, asexp)

    @staticmethod
    def same_usefulize(average, uncertainty):
        average = average.value if type(average) == Usefulnum else average
        uncertainty = Uncertainty(uncertainty) if type(uncertainty) != Uncertainty else uncertainty
        exponent = int('{0:e}'.format(average).split('e')[1])
        if uncertainty.coef == '0':
            return Usefulnum(average)
        else:
            return Usefulnum(average, exponent - uncertainty.exponent + uncertainty.usefulindex)


class Uncertainty(Usefulnum):
    @staticmethod
    def sround(numstr: str) -> tuple:
        if not (numstr.startswith('1') or numstr.startswith('2')):
            if abs(float(numstr) - int(float(numstr))) < 0.001:
                return (numstr[0], 1)
            else:
                return (str(int(numstr[0]) + 1), 1)
        else:
            if abs(float(numstr) - round(float(numstr), 1)) < 0.001:
                num = numstr[:3]
            else:
                tmp = str(int(numstr[0] + numstr[2]) + 1)
                num = tmp[:-1] + '.' + tmp[-1]
            return (num, 2)

    def __init__(self, value: int | float, equip_delta: float = 0, C=sqrt(3)):
        try:
            if type(value) == Uncertainty:
                self.coef = value.coef
                self.exponent = value.exponent
                self.usefulindex = value.usefulindex
                self.negetive = value.negetive
                self.finalexp = value.finalexp
                self.initvalue = value.initvalue
                self.value = value.value
            elif type(value) == Usefulnum:
                value = sqrt(value.value ** 2 + (equip_delta / C) ** 2)
                num = '{0:e}'.format(value)
                coef, exponent = tuple(num.split('e'))
                self.negetive = '± '
                coef = coef[1:] if coef.startswith('-') else coef
                coef, self.usefulindex = self.sround(coef)
                if not coef.startswith('10'):
                    self.coef = coef
                    self.exponent = int(exponent)
                elif coef == '10':
                    self.coef = '1'
                    self.exponent = int(exponent) + 1
                else:
                    self.coef = '1.0' + coef[3:-1]
                    self.exponent = int(exponent) + 1
                if self.coef.startswith('3.0'):
                    self.coef = '3'
                    self.usefulindex = 1
                self.initvalue = value
                self.value = float(coef + 'e' + exponent)
                self.finalexp = int(exponent) - self.usefulindex + 1
            else:
                if type(value) != int and type(value) != float:
                    raise Exception('value\'type must be int or float')
                value = sqrt(value ** 2 + (equip_delta / C) ** 2)
                num = '{0:e}'.format(value)
                coef, exponent = tuple(num.split('e'))
                self.negetive = '± '
                coef = coef[1:] if coef.startswith('-') else coef
                coef, self.usefulindex = self.sround(coef)
                if not coef.startswith('10'):
                    self.coef = coef
                    self.exponent = int(exponent)
                elif coef == '10':
                    self.coef = '1'
                    self.exponent = int(exponent) + 1
                else:
                    self.coef = '1.0' + coef[3:-1]
                    self.exponent = int(exponent) + 1
                if self.coef.startswith('3.0'):
                    self.coef = '3'
                    self.usefulindex = 1
                self.initvalue = value
                self.value = float(coef + 'e' + exponent)
                self.finalexp = int(exponent) - self.usefulindex + 1
        except Exception as error:
            print('Usefulnum.__init__ function raise errow:', error)