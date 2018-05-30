"""
launcher.py parses cli args and run simulator in appropriately mode
"""

import argparse
import fuzzysim
import fuzzysim.charts
import mamdani.generator
import importlib
import fuzzysim.charts
import time
import json

plot_parser = argparse.ArgumentParser(description='Fuzzysim plot launcher cli')
plot_parser.add_argument('csv_file', type=str, help="csv file name")

gen_parser = argparse.ArgumentParser(description='Fuzzysim config generator launcher cli')
gen_parser.add_argument('csv_file', type=str, help="csv file name")
gen_parser.add_argument('terms', type=int, help="generation terms conut")
gen_parser.add_argument('-i', '--interval', action='store_true', dest='interval', default=False, help="interval a")

sim_parser = argparse.ArgumentParser(description='Fuzzysim simulator launcher cli')
sim_parser.add_argument('distance', type=int, help="initial distance, meters")
sim_parser.add_argument('speed', type=int, help="initial speed, m/s")
sim_parser.add_argument('-w', '--way', type=str, dest='way_config_file', default='', help="way config file")
sim_parser.add_argument('-l', '--latency', type=float, dest='latency', default=0, help="acceleration appying latency, seconds")
sim_parser.add_argument('-c', '--controller', type=str, dest='brake_controller', default='dumb', help="brake controller module")
sim_parser.add_argument('-n', '--noplot', action='store_true', dest='noplot_graphs', default=False, help="Don't plot graphs")
sim_parser.add_argument('-s', '--stats', action='store_true', dest='print_stats', default=False, help="Print stats csv into stdout")
sim_parser.add_argument('-g', '--generate', dest='generate_csv', type=str, default="", help="generate rules from csv")
sim_parser.add_argument('-t', '--terms', dest='terms', type=int, default="3", help="generation terms conut")


def generate(argv):
	args = gen_parser.parse_args(argv)
	config = mamdani.generator.generate_config(args.csv_file, args.terms, args.interval)
	print(json.dumps(config, indent=4))



def launch(argv):
	args = sim_parser.parse_args(argv)

	simulate(
		args.distance,
		args.speed,
		args.latency,
		args.way_config_file,
		args.brake_controller,
		not args.noplot_graphs,
		args.print_stats
	)


def plot(argv):
	args = plot_parser.parse_args(argv)
	fuzzysim.charts.show_charts_csv(args.csv_file)


def simulate(distance, speed, latency, way_config_file, brake_controller, is_plot_graphs, is_print_stats):
	brake_module = importlib.import_module("brake_controller." + brake_controller)

	# print(brake_module.dumb)

	way_config = fuzzysim.WayConfig()

	way_config._obstacles = [
		fuzzysim.Obstacle(62, 40, None, 0),
		fuzzysim.Obstacle(30, 20, -2, None)
	]

	physics = fuzzysim.PhysModel(distance, speed, way_config, latency)
	controller = fuzzysim.CartController(physics, brake_module, 0)
	simulator = fuzzysim.Simulator(physics, controller)

	start = time.time()
	result, t, s, v, a = simulator.start()
	stop = time.time()

	if is_print_stats:
		print_stats(simulator)
	else:
		if result:
			print("============= Platform successfully stopped! =============")
		else:
			print("!!!!!!!!!!!!!!!!!!! Platform CRASHED !!!!!!!!!!!!!!!!!!!!!")

		print("T: %.3f    S: %.3f    V: %.3f    a: %.3f" % (t, s, v, a))
		print("Simulation time: %.3f seconds" % (stop - start))

	if is_plot_graphs:
		fuzzysim.charts.show_charts_simulator(simulator)


def get_obstacles_from_file(filename):
	# TODO
	return None


def print_stats(simulator):
	stats_t, stats_s, stats_v, stats_a, stats_j = simulator.stats_t, simulator.stats_s, simulator.stats_v, simulator.stats_a, simulator.stats_j

	print("t,s,v,a,j")
	for i, v in enumerate(stats_t):
		print("%.4f,%.4f,%.4f,%.4f,%.4f" %  (stats_t[i], stats_s[i], stats_v[i], stats_a[i], stats_j[i]))
