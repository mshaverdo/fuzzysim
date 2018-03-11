import matplotlib.pyplot as plt
import csv
import pprint
import math
import mamdani


def plot_datasets(datasets):
	"""
	Plot charts for provided datasets

	:param datasets: [{'x': X_points, 'y': Y_points, 'xl': 'X Label', 'yl': 'Y lable'},]
	:return:
	"""

	# plt.grid(True)

	for ds in datasets:
		(f, ax) = plt.subplots()

		ax.grid(True)

		if 'xl' in ds:
			ax.set_xlabel(ds['xl'])
		if 'yl' in ds:
			ax.set_ylabel(ds['yl'])

		if 'xl' in ds and 'yl' in ds:
			title = "%s from %s" % (ds['yl'], ds['xl'])
			f.canvas.set_window_title(title)

		if 'x' in ds:
			title = "%s from %s" % (ds['yl'], ds['xl']) if 'title' not in ds else ds['title']
			f.canvas.set_window_title(title)
			marker = 'y1m' in ds and ds['y1m'] or None
			ax.plot(ds['x'], ds['y'], label=ds['yl'], marker=marker)
		if 'x2' in ds:
			# label = "y2" if 'y2l' not in ds else ds['y2l']
			label = 'y2l' in ds and ds['y2l'] or 'y2'
			marker = 'y2m' in ds and ds['y2m'] or None
			ax.plot(ds['x2'], ds['y2'], label=label, marker=marker)
			ax.legend()
		if 'x3' in ds:
			# label = "y3" if 'y3l' not in ds else ds['y3l']
			label = 'y3l' in ds and ds['y3l'] or 'y3'
			marker = 'y3m' in ds and ds['y3m'] or None
			ax.plot(ds['x3'], ds['y3'], label=label, marker=marker)
			ax.legend()

		if 'sub' in ds:
			for sub in ds['sub']:
				# ax.set_ylabel(sub['yl'])
				# ax.set_xlabel(sub['xl'])
				# title = "%s from %s" % (sub['yl'], sub['xl']) if 'title' not in sub else sub['title']
				# f.canvas.set_window_title(title)

				label = 'yl' in sub and sub['yl']
				marker = 'ym' in sub and sub['ym'] or None
				ax.plot(sub['x'], sub['y'], label=label, marker=marker)
				ax.legend()

		ax.spines['left'].set_position('zero')
		ax.spines['bottom'].set_position('zero')
		ax.spines['left'].set_smart_bounds(True)
		ax.spines['bottom'].set_smart_bounds(True)

	plt.show()


def get_datasets(stats_t, stats_s, stats_v, stats_a, stats_j):
	return [
		{'x': stats_t, 'y': stats_s, 'xl': 'Time, s', 'yl': 'Distance, m'},
		{'x': stats_t, 'y': stats_v, 'xl': 'Time, s', 'yl': 'Speed, m/s'},
		{'x': stats_t, 'y': stats_a, 'xl': 'Time, s', 'yl': 'Acceleration, m/s^2'},
		{'x': stats_t, 'y': stats_j, 'xl': 'Time, s', 'yl': 'J, m/s^3'},
		# {'x': stats_s, 'y': stats_a, 'xl': 'S, m', 'yl': 'A, m/s^2'},
		# {'x': stats_t, 'y': stats_k, 'xl': 'Time, s', 'yl': 'K, m/s^3'},
		# {'x': stats_, 'y': stats_, 'xl': 'Time, s', 'yl': ''},
	]


def show_charts_csv(csv_file_name):
	experiments = []
	experiment = None
	with open(csv_file_name, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='\\')
		for row in reader:
			if row[0] == "t":
				# new experiment
				if experiment is not None:
					experiments.append(experiment)
				experiment = {'stats_t': [], 'stats_s': [], 'stats_v': [], 'stats_a': [], 'stats_j': []}
				continue

			experiment['stats_t'].append(float(row[0]))
			experiment['stats_s'].append(float(row[1]))
			experiment['stats_v'].append(float(row[2]))
			experiment['stats_a'].append(float(row[3]))
			experiment['stats_j'].append(float(row[4]))

	experiments.append(experiment)

	datasets = []
	for en, experiment in enumerate(experiments):
		experiment_datasets = get_datasets(**experiment)

		for i, ds in enumerate(experiment_datasets):
			if i == len(datasets):
				datasets.append({'sub': []})

			datasets[i]['xl'] = ds['xl']
			datasets[i]['yl'] = ds['yl']
			ds['yl'] = "(%d) %s" % (en, ds['yl'])
			datasets[i]['sub'].append(ds)

	show_stats(experiments)
	plot_datasets(datasets)


def show_stats(experiments):
	if len(experiments) < 2:
		return

	gauge = experiments[0]
	stats = {'stats_s':{}, 'stats_v':{}, 'stats_a':{}, 'stats_j':{}}
	for en, experiment in enumerate(experiments):
		for param in stats:
			sum = 0
			for i, s in enumerate(experiment[param]):
				G = len(gauge[param]) > i and gauge[param][i] or 0
				sum += (s - G)**2
			sum /= len(experiment[param])
			stats[param][en] = math.sqrt(sum)

	print("Normalized quadratic Parameters deviations by experiment:")
	pprint.pprint(stats)


def show_charts_simulator(simulator):
	"""
	Prepare datasets and plot it
	"""
	stats_t, stats_s, stats_v, stats_a, stats_j = simulator.stats_t, simulator.stats_s, simulator.stats_v, simulator.stats_a, simulator.stats_j
	datasets = get_datasets(stats_t, stats_s, stats_v, stats_a, stats_j)
	plot_datasets(datasets)


def setup_variables(variables):
	for i, variable in enumerate(variables):
		ax = plt.subplot(len(variables), 1, i+1)
		ax.grid(True)
		ax.set_title("Variable: %s" % variable.name, loc='left')
		ax.spines['bottom'].set_position('zero')
		ax.spines['left'].set_position('zero')

		for t in variable.terms.values():
			c = min(t.c, variable.max)
			d = min(t.d, variable.max)
			plt.plot([t.a, t.b, c, d], [0, t.height, t.height, 0])


def show_vars(alg: mamdani.MamdaniAlgorithm):
	f = plt.figure(1)
	f.suptitle("Out variables")
	setup_variables(alg.in_variables.values())

	f = plt.figure(2)
	f.suptitle("In Variables")
	setup_variables(alg.out_variables.values())

	plt.show()

