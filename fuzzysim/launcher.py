"""
launcher.py parses cli args and run simulator in appropriately mode
"""

import argparse
import fuzzysim
import fuzzysim.charts
import importlib

parser = argparse.ArgumentParser(description='Fuzzysim launcher cli')
parser.add_argument('distance', type=int, help="initial distance, meters")
parser.add_argument('speed', type=int, help="initial speed, m/s")
parser.add_argument('-w', '--way', type=str, dest='way_config_file', default='', help="way config file")
parser.add_argument('-l', '--latency', type=float, dest='latency', default=0, help="acceleration appying latency, seconds")
parser.add_argument('-c', '--controller', type=str, dest='brake_controller', default='dumb', help="brake controller module")
parser.add_argument('-p', '--plot', type=bool, dest='plot_graphs', default=True, help="Plot graphs")
parser.add_argument('-s', '--stats', type=bool, dest='print_stats', default=False, help="Print stats csv into stdout")


def launch(argv):
	args = parser.parse_args(argv)
	simulate(
		args.distance,
		args.speed,
		args.latency,
		args.way_config_file,
		args.brake_controller,
		args.plot_graphs,
		args.print_stats
	)


def simulate(distance, speed, latency, way_config_file, brake_controller, plot_graphs, print_stats):
	brake_module = importlib.import_module("brake_controller.dumb")

	# print(brake_module.dumb)

	way_config = fuzzysim.WayConfig()
	physics = fuzzysim.PhysModel(distance, speed, way_config, latency)
	controller = fuzzysim.CartController(physics, brake_module, 0)
	simulator = fuzzysim.Simulator(physics, controller)

	result, t, s, v, a = simulator.start()

	if print_stats:
		print_stats(simulator)
	else:
		if result:
			print("============= Platform successfully stopped! =============")
		else:
			print("!!!!!!!!!!!!!!!!!!! Platform CRASHED !!!!!!!!!!!!!!!!!!!!!")

		print("T: %.3f    S: %.3f    V: %.3f    a: %.3f" % (t, s, v, a))

	if plot_graphs:
		fuzzysim.charts.show_charts_simulator(simulator)


def get_obstacles_from_file(filename):
	# TODO
	return None


def print_stats(simulator):
	stats_t, stats_s, stats_v, stats_a, stats_j = simulator.stats_t, simulator.stats_s, simulator.stats_v, simulator.stats_a, simulator.stats_j

	print("t,s,v,a")
	for i, v in enumerate(stats_t):
		print("%.4f,%.4f,%.4f,%.4f,%.4f," %  (stats_t[i], stats_s[i], stats_v[i], stats_a[i], stats_j[i]))