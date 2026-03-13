import re

class Unit:
    ISUdic = {'constant': '1', 'angle': 'rad', 'length': 'm', 'mass': 'kg', 'time': 's', 'electricity': 'A', 'temperature': 'K', 'amount': 'mol', 'light': 'cd'}
    basic_typedic = { '': 'constant',    '1': 'constant',
        'rad': 'angle',    '°': 'angle',    'pi': 'angle',   'π': 'angle',
        'km': 'length',    'm': 'length',   'dm': 'length',  'cm': 'length',
        'mm': 'length',    'nm': 'length',  'um': 'length',  'pm': 'length',
        't': 'mass',       'kg': 'mass',    'g': 'mass',     'mg': 'mass',
        'h': 'time',       'min': 'time',   's': 'time',     'ms': 'time',
        'A': 'electricity',
        'mol': 'amount',
        '℃': 'temperature', '℉': 'temperature', 'K': 'temperature',
        '°C': 'temperature', '°F': 'temperature',
        'cd': 'light',
        'mV': 'volent'
    }
    sub_typedic = {'N': {'kg': 2, 'm': 1, 's': -2}, 'pa': {'kg': 1, 'm': -1, 's': -2}, 'hz': {'s': -1},
                   'mV': {},}

    @staticmethod
    def reshape_unitdict(unitdic: dict) -> dict:
        newunitdic1 = {}
        newunitdic2 = {}
        for index, value in unitdic.items():
            if value != 0:
                newunitdic1[index] = value
        if not newunitdic1:
            return {'1': 1}
        if len(newunitdic1) > 1 and not ('1' in newunitdic1.keys() and '' in newunitdic1.keys()):
            for index, value in newunitdic1.items():
                if index != '' and index != '1':
                    newunitdic2[index] = value
            return newunitdic2
        elif '1' in newunitdic1.keys() or '' in newunitdic1.keys():
            return {'1': 1}
        else:
            return newunitdic1

    @staticmethod
    def split_complex_unit(ustr: str) -> dict:
        try:
            unitdic = {}
            if '**' in ustr:
                ustr = re.sub('\*\*', '^', ustr)
            if '/' in ustr:
                lst1 = ustr.split('/')
                if len(lst1) > 2:
                    raise Exception('Illegal expression,please check \'\\\'')
                else:
                    ustr = lst1[0]
                    if lst1[1].startswith('(') and lst1[1].endswith(')'):
                        lst1 = lst1[1].lstrip('(').rstrip(')').split('*')
                        for item in lst1:
                            if '^' in item:
                                lst2 = item.split('^')
                                if len(lst2) > 2:
                                    raise Exception('Illegal expression,please check \'^\'')
                                elif lst2[0] not in Unit.basic_typedic:
                                    raise Exception('Fail to find unit:{0}'.format(lst2[0]))
                                elif type(eval(lst2[1])) != int:
                                    raise Exception('Illegal expression,please check {0}'.format(item))
                                else:
                                    unitdic[lst2[0]] = unitdic[lst2[0]] - int(lst2[1]) if lst2[0] in unitdic.keys() else -int(lst2[1])
                            else:
                                unitdic[item] = unitdic[item] - 1 if item in unitdic.keys() else -1
                    else:
                        if '^' in lst1[1]:
                            lst2 = lst1[1].split('^')
                            if len(lst2) > 2:
                                raise Exception('Illegal expression,please check \'^\'')
                            elif lst2[0] not in Unit.basic_typedic:
                                raise Exception('Fail to find unit:{0}'.format(lst2[0]))
                            elif type(eval(lst2[1])) != int:
                                raise Exception('Illegal expression,please check {0}'.format(item))
                            else:
                                unitdic[lst2[0]] = unitdic[lst2[0]] - int(lst2[1]) if lst2[0] in unitdic.keys() else -int(lst2[1])
                        else:
                            unitdic[lst1[1]] = unitdic[lst1[1]] - 1 if lst1[1] in unitdic.keys() else -1
            lst1 = ustr.split('*')
            for item in lst1:
                if '^' in item:
                    lst2 = item.split('^')
                    if len(lst2) > 2:
                        raise Exception('Illegal expression,please check \'^\'')
                    elif lst2[0] not in Unit.basic_typedic:
                        raise Exception('Fail to find unit:{0}'.format(lst2[0]))
                    elif type(eval(lst2[1])) != int:
                        raise Exception('Illegal expression,please check {0}'.format(item))
                    else:
                        unitdic[lst2[0]] = unitdic[lst2[0]] + int(lst2[1]) if lst2[0] in unitdic.keys() else int(lst2[1])
                else:
                    unitdic[item] = unitdic[item] + 1 if item in unitdic.keys() else 1
            return Unit.reshape_unitdict(unitdic)
        except Exception as error:
            print('Unit.split_complex_unit raise error:', error)
            return False

    @staticmethod
    def reshape_ustr(unitdic: dict) -> str:
        typelist = []
        for item in unitdic.items():
            tmpt = (item[1], item[0])
            typelist.append(tmpt)
        typelist.sort(reverse=True)
        if len(typelist) == 1:
            if typelist[0][1] == '1' or typelist[0][1] == '':
                return ''
            elif typelist[0][0] == 1:
                return typelist[0][1]
            else:
                return '{0}^{1}'.format(typelist[0][1], typelist[0][0])
        else:
            ustr = typelist[0][1] if typelist[0][0] == 1 else '{0}^{1}'.format(typelist[0][1], typelist[0][0])
            for item in typelist[1:]:
                ustr += '*' + (item[1] if item[0] == 1 else '{0}^{1}'.format(item[1], item[0]))
            return ustr

    def __init__(self, ustr: str | dict = 'constant', ISU: bool = False):
        try:
            if type(ustr) == Unit:
                self.str = ustr.str
                self.unitdic = Unit.reshape_unitdict(ustr.unitdic)
                self.ISU = ustr.ISU
                self.stable_str = Unit.reshape_ustr(self.unitdic)
            elif type(ustr) == dict:
                self.unitdic = Unit.reshape_unitdict(ustr)
                self.str = Unit.reshape_ustr(self.unitdic)
                self.ISU = ISU
                self.stable_str = Unit.reshape_ustr(self.unitdic)
            else:
                if ISU:
                    self.unitdic = {Unit.ISUdic[ustr]: 1}
                    self.str = Unit.ISUdic[ustr]
                    self.stable_str = Unit.reshape_ustr(self.unitdic)
                else:
                    if ustr in Unit.ISUdic.values():
                        self.str = ustr
                        self.unitdic = {ustr: 1}
                        self.ISU = True
                        self.stable_str = Unit.reshape_ustr(self.unitdic)
                    elif Unit.split_complex_unit(ustr):
                        if not Unit.split_complex_unit(ustr):
                            raise Exception('Unit.split_complex_unit raise error')
                        self.unitdic = Unit.split_complex_unit(ustr)
                        self.str = ustr
                        self.ISU = False
                        self.stable_str = Unit.reshape_ustr(self.unitdic)
                    else:
                        raise Exception('Fail to find unit:{0}'.format(ustr))
        except Exception as error:
            print('Unit.__init__ function raise errow:', error)

    def __str__(self) -> str:
        return self.stable_str

    def __repr__(self) -> str:
        return self.str

    def __mul__(self, unt):
        unt = Unit(unt) if type(unt) != Unit else unt
        newudic = self.unitdic.copy()
        for key in unt.unitdic.keys():
            if key in newudic.keys():
                newudic[key] += unt.unitdic[key]
            else:
                newudic[key] = unt.unitdic[key]
        newudic = Unit.reshape_unitdict(newudic)
        return Unit(newudic)

    def __truediv__(self, unt):
        unt = Unit(unt) if type(unt) != Unit else unt
        newudic = self.unitdic.copy()
        for key in unt.unitdic.keys():
            if key in newudic.keys():
                newudic[key] = newudic[key] - unt.unitdic[key]
            else:
                newudic[key] = -unt.unitdic[key]
        newudic = Unit.reshape_unitdict(newudic)
        return Unit(newudic)

    def __pow__(self, num: int):
        try:
            newudic = {}
            if type(num) != int:
                raise Exception('The exponent should be int type')
            for key in self.unitdic.keys():
                newudic[key] = num * self.unitdic[key]
            newudic = Unit.reshape_unitdict(newudic)
            return Unit(newudic)
        except Exception as error:
            print('Unit.__pow__ raise error:', error)

    def usqrt(self):
        try:
            newudic = {}
            for key in self.unitdic.keys():
                if self.unitdic[key] % 2 != 0:
                    raise Exception('The exponent can\'t be float type')
                newudic[key] = int(self.unitdic[key] / 2)
            newudic = Unit.reshape_unitdict(newudic)
            return Unit(newudic)
        except Exception as error:
            print('Unit.__pow__ raise error:', error)