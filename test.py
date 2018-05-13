import fuzzysim.launcher
import fuzzysim.charts
import sys

v = 20
dataset = {'x': [], 'y': [], 'xl': 'X Label', 'yl': 'Y lable'}
for s in range(1, 100):
	const_a = -v ** 2 / (2 * s)
	dataset['x'].append(s)
	dataset['y'].append(const_a)

fuzzysim.charts.plot_datasets([dataset])
