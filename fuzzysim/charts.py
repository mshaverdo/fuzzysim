import matplotlib.pyplot as plt
import csv
import pprint


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

		if 'x' in ds:
			ax.set_ylabel(ds['yl'])
			ax.set_xlabel(ds['xl'])
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
			ds['yl'] = "(%d) %s" % (en, ds['yl'])
			if i == len(datasets):
				datasets.append({'sub': []})
			datasets[i]['sub'].append(ds)

	plot_datasets(datasets)


def show_charts_simulator(simulator):
	"""
	Prepare datasets and plot it
	"""
	stats_t, stats_s, stats_v, stats_a, stats_j = simulator.stats_t, simulator.stats_s, simulator.stats_v, simulator.stats_a, simulator.stats_j
	datasets = get_datasets(stats_t, stats_s, stats_v, stats_a, stats_j)
	plot_datasets(datasets)
