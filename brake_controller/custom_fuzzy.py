import math
from mamdani import Term, Variable, Rule, Cond, MamdaniAlgorithm, IntervalTerm
import fuzzysim.charts
import json


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
		self.alg = load_mamdani(None)
		self.normalized = False
		fuzzysim.charts.show_vars(self.alg)

	def get_a(self, current_s, current_v):
		if not self.normalized:
			self.normalized = True
			current_const_a = current_v ** 2 / (2 * current_s)
			self.alg = load_mamdani(None, current_const_a)
			fuzzysim.charts.show_vars(self.alg)

		out = self.alg.process({'S': current_s, 'V': current_v})
		return -out['A']


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
