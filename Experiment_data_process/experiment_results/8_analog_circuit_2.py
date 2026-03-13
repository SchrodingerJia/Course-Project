from utils.plotting import getcurves

# 模电实验二：方波、三角波发生器
pi = 3.1415927
# 方波发生器
uos = (6, 2 * pi * 0.4353, 'sqr', 't', 'uo', 'blue', 'uo\namplitude=±6.0V\nduty ratio=47.64%')
ucs = (3, 2 * pi * 0.4353, 'tri', 't', 'uc', 'red', 'ui\namplitude==±3.0V\nf=435.3Hz')
getcurves([uos, ucs], 'ms', 'V', 't', 'U', 'Square-wave generator')

# 三角波发生器
uot = (1, 2 * pi * 1.002, 'tri', 't', 'uo', 'blue', 'uo\nT=0.999ms\namplitude==±1.0V')
uo1t = (6, 2 * pi * 1.002, 'sqr', 't', 'uo1', 'red', 'uo1\nf=1.002kHz\nduty ratio=52.97%')
getcurves([uot, uo1t], 'ms', 'V', 't', 'U', 'Triangle-wave generator')

# 自设计发生器
uod = (2, 2 * pi * 0.7233, 'tri', 't', 'uo', 'blue', 'uo\namplitude==±2.0V\nf=723.3Hz')
uo1d = (6, 2 * pi * 0.7233, 'sqr', 't', 'uo1', 'red', 'uo1\namplitude==±6.0V\nduty ratio=47.55%')
getcurves([uod, uo1d], 'ms', 'V', 't', 'U', 'Designed generator')