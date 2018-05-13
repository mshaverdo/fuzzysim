import math
from mamdani import Term, Variable, Rule, Cond, MamdaniAlgorithm, IntervalTerm
import fuzzysim.charts
import json
import brake_controller.naive


def load_mamdani(config_file=None, current_const_a=None):
	if config_file is None:
		config_file="fuzzy.json"

	config = {
		'S': {
			'min': 0,
			'max': 100,
			'peaks': [25, 75,],
		},
		'V': {
			'min': 0,
			'max': 20,
			'peaks': [5, 15,],
		},
		'A': {
			'min': 0,
			'max': 7,
			'peaks': [0, 4.75, 7],
		},
		'rules': [
			{'conds': [['S', 0], ['V', 0]], 'concs': [['A', 0],]},
			{'conds': [['S', 0], ['V', 1]], 'concs': [['A', 1],]},
			{'conds': [['S', 1], ['V', 0]], 'concs': [['A', 0],]},
			{'conds': [['S', 1], ['V', 1]], 'concs': [['A', 0],]},
		]
	}

	config = json.load(open(config_file))
	if current_const_a is not None:
		src_const_a = config['V']['max'] ** 2 / (2 * config['S']['max'])
		ratio = current_const_a / src_const_a
		config['A']['peaks'] = [i * ratio for i in config['A']['peaks']]
		config['A']['max'] *= ratio

	in_variables = {
		'S': get_variable('S', config['S']),
		'V': get_variable('V', config['V']),
	}
	out_variables = {'A':get_variable('A', config['A']), }

	rules = get_rules({**in_variables, **out_variables}, config['rules'])

	return MamdaniAlgorithm(in_variables.values(), out_variables.values(), rules)


def get_variable(name, config):
	is_interval = 'interval' in config and config['interval']

	terms = []
	inf = float(math.inf)
	for i, peak in enumerate(config['peaks']):
		if i == 0:
			a, b = config['min'], config['min']
		else:
			a, b = config['peaks'][i - 1], peak

		if i == len(config['peaks']) - 1:
			c, d = config['max'], config['max']
		else:
			c, d = peak, config['peaks'][i + 1]

		if is_interval:
			terms.append(IntervalTerm(get_term_name(name, i), (a+b)/2, (c+d)/2))
		else:
			terms.append(Term(get_term_name(name, i), a, b, c, d))

	return Variable(name, terms, config['min'], config['max'])


def get_term_name(var_name, n):
	return "%s%d" % (var_name, n)


def get_rules(vars, config):
	rules = []
	for v in config:
		conditions = []
		for c in v['conds']:
			conditions.append(Cond(vars[c[0]], vars[c[0]].terms[get_term_name(*c)]))
		conclusions = []
		for c in v['concs']:
			conclusions.append(Cond(vars[c[0]], vars[c[0]].terms[get_term_name(*c)]))

		rules.append(Rule(conditions, conclusions))

	return rules


class Controller:
	def __init__(self):
		self.gold_controller = brake_controller.naive
		self.gold_v = 0
		self.gold_s = 0
		self.gold_a = 0
		self.alg = load_mamdani(None)
		self.normalized = True
		fuzzysim.charts.show_vars(self.alg)

	def normalize(self, current_s, current_v):
		self.normalized = True
		current_const_a = current_v ** 2 / (2 * current_s)
		self.alg = load_mamdani(None, current_const_a)
		fuzzysim.charts.show_vars(self.alg)

	def get_a(self, current_s, current_v):
		if not self.normalized:
			self.normalize(current_s, current_v)

		if self.gold_a == 0:
			self.gold_s = current_s
			self.gold_v = current_v

		self.process_gold()

		if abs(self.gold_v - current_v) > 0.01 * self.gold_v:
			current_const_a = current_v ** 2 / (2 * current_s)
			# return math.copysign(self.gold_a, self.gold_v - current_v)
			# return math.copysign(self.gold_controller.const_a * 2, self.gold_v - current_v)
			# return math.copysign(current_const_a * 2, self.gold_v - current_v)
			return min(0.0, math.copysign(current_const_a * 2, self.gold_v - current_v))

		out = self.alg.process({'S': current_s, 'V': current_v})
		return -out['A']

	def process_gold(self):
		self.gold_a = self.gold_controller.get_a(self.gold_s, self.gold_v, self.gold_a)

		self.gold_v += self.gold_a * self.gold_controller.time_quantum
		self.gold_s -= self.gold_v * self.gold_controller.time_quantum + (self.gold_a * self.gold_controller.time_quantum ** 2) / 2


default_controller = Controller()


def get_a(current_s, current_v, current_a):
	current_v = max(current_v, 0)
	current_s = max(current_s, 0)

	if current_v == 0:
		return 0
	a = default_controller.get_a(current_s, current_v)
	return a


if __name__ == '__main__':
	alg = load_mamdani(None)
	fuzzysim.charts.show_vars(alg)
