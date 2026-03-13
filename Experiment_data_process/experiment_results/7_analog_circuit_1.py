from utils.plotting import getsubcurves, getcurves

# 模电实验一：减法器、积分器、微分器
pi = 3.1415927
f = 1
omega = 2 * pi * f
# 减法器
uos = (0.99, omega, 0, 't', 'uo', 'yellow', 'uo')
ui2s = (0.99, omega, 0, 't', 'ui2', 'blue', 'ui2')
getsubcurves([uos, ui2s], 'ms', 'V', 't', 'U', 'Subtracter Ui2=1V')

uos = (2.99, omega, 0, 't', 'uo', 'yellow', 'uo')
ui2s = (1.98, omega, 0, 't', 'ui2', 'blue', 'ui2')
getsubcurves([uos, ui2s], 'ms', 'V', 't', 'U', 'Subtracter Ui2=2V')

# 积分器与微分器
uoi = (2.4, omega, 'tri', 't', 'uo', 'blue', 'uo\namplitude=4.8V')
uii = (1, omega, 'sqr', 't', 'ui2', 'red', 'ui\namplitude=2.0V')
getcurves([uoi, uii], 'ms', 'V', 't', 'U', 'Integrator')

uod = (0.41, omega, 'sqr', 't', 'uo', 'blue', 'uo\namplitude=0.82V')
uid = (1, omega, 'tri', 't', 'ui2', 'red', 'ui\namplitude=2.0V')
getcurves([uod, uid], 'ms', 'V', 't', 'U', 'Differentiator')