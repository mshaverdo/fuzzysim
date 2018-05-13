import csv
import sys
import operator
import numpy


def generate_config(csv_file_name, terms_count, is_interval):
	data = {'S': [], 'V': [], 'A': []}

	with open(csv_file_name, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='\\')
		cols = {}
		for row in reader:
			if row[0] == "t":
				cols = {v.upper(): i for i, v in enumerate(row)}
				continue

			# data['T'].append(float(row[0]))
			data['S'].append(float(row[cols['S']]))
			data['V'].append(float(row[cols['V']]))
			data['A'].append(abs(float(row[cols['A']])))
		# data['J'].append(float(row[4]))

	maxs = {k: max(v) for k, v in data.items()}
	mins = {k: min(v) for k, v in data.items()}
	steps = {k: abs(maxs[k] - mins[k]) / terms_count for k, v in maxs.items()}

	config = {
		'S': get_var_config(maxs['S'], mins['S'], steps['S'], 0),
		'V': get_var_config(maxs['V'], mins['V'], steps['V'], 0),
		'A': get_var_config(maxs['A'], mins['A'], steps['A'], is_interval),
		'rules': generate_rules(data, ['S', 'V'], ['A'], terms_count)
	}

	a_map = print_map(config, terms_count)
	for s, speeds in enumerate(a_map):
		begin = True
		for v, a in enumerate(speeds):
			if a != ' ':
				begin = False
				continue

			if begin:
				# a_map[s][v] = 0
				config['rules'].append({'conds': [['S', s], ['V', v]], 'concs': [['A', 0],]})
			else:
				config['rules'].append({'conds': [['S', s], ['V', v]], 'concs': [['A', terms_count - 1],]})

	print("\n", file=sys.stderr, sep='')
	print_map(config, terms_count)

	return config

def print_map(config, terms_count):
	a_map = []
	for i in range(0, terms_count):
		a_map.append([])
		for j in range(0, terms_count):
			a_map[i].append(' ')

	for r in config['rules']:
		m = {}
		for c in r['conds']:
			m[c[0]] = c[1]

		v = str(r['concs'][0][1])
		a_map[m['S']][m['V']] = v

	print('S\\V', [str(i) for i in range(0, terms_count)], file=sys.stderr, sep='')
	for i, row in enumerate(a_map):
		print("%03d" % i, row, file=sys.stderr, sep='')

	return a_map


def get_var_config(var_max, var_min, var_step, interval):
	return {
			'min': var_min,
			'max': var_max,
			'peaks': list(numpy.arange(var_min + var_step / 2, var_max, var_step)),
			'interval': interval
		}


def generate_rules(data, in_vars, out_vars, terms_count):
	rules = {}

	maxs = {k: max(v) for k, v in data.items()}
	mins = {k: min(v) for k, v in data.items()}
	steps = {k: abs(maxs[k] - mins[k]) / terms_count for k, v in maxs.items()}

	for i, _ in enumerate(list(data.values())[0]):
		terms = []
		for k, stat in data.items():
			max_term = int(abs(maxs[k] - mins[k]) / steps[k]) - 1
			terms.append([k, min(max_term, int(abs(stat[i] - mins[k]) / steps[k]))])

		in_terms = tuple(tuple(v) for v in terms if v[0] in in_vars)
		out_terms = tuple(tuple(v) for v in terms if v[0] in out_vars)

		# if in_terms in rules and rules[in_terms] != out_terms:
		# 	raise ValueError("Failed to add rule: in: %s, existing out : %s, new out: %s" % (in_terms, rules[in_terms], out_terms))

		if in_terms not in rules:
			rules[in_terms] = {}

		if out_terms not in rules[in_terms]:
			rules[in_terms][out_terms] = 0

		rules[in_terms][out_terms] += 1

	# rules[in_terms] = out_terms

	return list([{'conds': k, 'concs': max(v.items(), key=lambda x: x[1])[0]} for k, v in rules.items()])


if __name__ == "__main__":
	print(generate_config('golden.csv', 3))
