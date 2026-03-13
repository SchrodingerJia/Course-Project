from utils.plotting import getcurves

# 电路实验四：交流电路波形
pi = 3.1415927
Uls = (55.1, 2 * pi * 50, 0, 't', 'U', 'red', 'U-loop-short\namplitude=55.1V')
Ils = (52, 2 * pi * 50, -2.72, 't', 'I', 'blue', 'I-loop-short\namplitude=52A')
getcurves([Uls, Ils], 'ms', 'U', 't', 'I', 'Loop-short curves  delta phi=-2.72')

Ulo = (65.5, 2 * pi * 50, 0, 't', 'U', 'red', 'U-loop-open\namplitude=65.5V')
Ilo = (50, 2 * pi * 50, 9.72, 't', 'I', 'blue', 'I-loop-open\namplitude=50.2A')
getcurves([Ulo, Ilo], 'ms', 'U', 't', 'I', 'Loop-open curves  delta phi=9.72')

Uus = (55.1, 2 * pi * 50, 0, 't', 'U', 'red', 'U-u-short\namplitude=55.1V')
Ius = (53, 2 * pi * 50, -1.15, 't', 'I', 'blue', 'I-u-short\namplitude=53A')
getcurves([Uus, Ius], 'ms', 'U', 't', 'I', 'U-short curves  delta phi=-1.15')

Uuo = (54.3, 2 * pi * 50, 0, 't', 'U', 'red', 'U-u-open\namplitude=54.3V')
Iuo = (52, 2 * pi * 50, -0.07, 't', 'I', 'blue', 'I-u-open\namplitude=52A')
getcurves([Uuo, Iuo], 'ms', 'U', 't', 'I', 'U-open curves  delta phi=-0.07')