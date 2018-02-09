import math
from scipy.integrate import quad
import time
import numpy


class Term:
	def __init__(self, name, a, b, c, d):
		self.name = name
		self.a = a
		self.b = b
		self.c = c
		self.d = d

	def degree(self, crisp_value):
		if self.a <= crisp_value <= self.b:
			return (crisp_value - self.a) / (self.b - self.a)
		elif self.b < crisp_value < self.c:
			return 1
		elif self.c <= crisp_value <= self.d:
			return (self.d - crisp_value) / (self.d - self.c)
		else:
			return 0


class Variable:
	def __init__(self, name, terms, min, max):
		self.name = name
		self.terms = {v.name: v for v in list(terms)}
		self.min = min
		self.max = max

	def get_fuzzy_value(self, crisp_value):
		"""

		:param crisp_value:
		:return: FuzzyValue
		"""
		memberships = {i: Membership(v, v.degree(crisp_value)) for i, v in self.terms.items()}
		return FuzzyValue(self, crisp_value, memberships)


class Membership:
	def __init__(self, term, degree):
		self.term = term
		self.degree = degree

	def __eq__(self, other):
		return self.term == other.term and self.degree == other.degree

	def __lt__(self, other):
		return self.degree < other.degree

	def __le__(self, other):
		return self.degree <= other.degree

	def __gt__(self, other):
		return self.degree > other.degree

	def __ge__(self, other):
		return self.degree >= other.degree

	def __str__(self):
		return "%s(%.2f)" % (self.term.name, self.degree)


class FuzzyValue:
	integration_delta_ratio = 0.01

	def __init__(self, variable, precise_value, memberships):
		self.variable = variable
		self.precise_value = precise_value
		self.memberships = {v.term.name: v for v in memberships.values()}

	def __str__(self):
		return "FuzzyValue(%s, %.2f, %s)" % (
			self.variable.name,
			self.precise_value or 0,
			list(str(v) for v in self.memberships.values())
		)

	def get_membership(self, term):
		return self.memberships[term.name]

	def add_membership(self, membership, unite=True):
		if membership.term.name in self.memberships and not unite:
			raise ValueError("Trying to add membership %s to fuzzyValue %s without uniting: "
							 "membership already defined in the value" % (membership, self))

		if membership.term.name not in self.memberships or membership > self.memberships[membership.term.name]:
			self.memberships[membership.term.name] = membership

	def degree(self, crisp_value):
		degree = 0
		for m in self.memberships.values():
			term_degree = min(m.degree, m.term.degree(crisp_value))
			degree = max(degree, term_degree)

		return degree

	def integrate(self, upto=None):
		delta = (self.variable.max - self.variable.min) * self.integration_delta_ratio
		result = 0
		for x in numpy.arange(self.variable.min, self.variable.max, delta):
			result += self.degree(x)
			if upto is not None and result > upto:
				return result, x

		return result

	def get_center_of_mass_fast(self):
		weight = self.integrate()
		_, center_x = self.integrate(weight/2)
		return center_x

	def get_center_of_mass(self):
		result1, err = quad(lambda x: x * self.degree(x), self.variable.min, self.variable.max)
		result2, err = quad(lambda x: self.degree(x), self.variable.min, self.variable.max)
		return result1 / result2


class Cond:
	def __init__(self, variable, term):
		self.variable = variable
		self.term = term


class Conclusion:
	def __init__(self, variable, term):
		self.variable = variable
		self.term = term


class Rule:
	def __init__(self, conditions, conclusions):
		self.conditions = conditions
		self.conclusions = conclusions


class MamdaniAlgorithm:
	def __init__(self, in_variables, out_variables, rules):
		self.in_variables = {v.name: v for v in in_variables}
		self.out_variables = {v.name: v for v in out_variables}
		self.rules = rules

	def fuzzificate(self, in_crisp_values):
		"""Returns map of FuzzyValues for provided precise values of input vars"""

		return {
			i: v.get_fuzzy_value(in_crisp_values[i])
			for i, v
			in self.in_variables.items()
		}

	def apply_rules(self, in_fuzzy_values):
		"""Returns lists of FuzzyValues, mapped to out_variables"""

		out_fuzzy_values = {}
		for r in self.rules:
			memberships = list(
				in_fuzzy_values[c.variable.name].get_membership(c.term)
				for c
				in r.conditions
			)
			activated_degree = min(memberships).degree

			for c in r.conclusions:
				if c.variable.name not in out_fuzzy_values:
					out_fuzzy_values[c.variable.name] = FuzzyValue(c.variable, None, {})

				out_fuzzy_values[c.variable.name].add_membership(Membership(c.term, activated_degree))

		return out_fuzzy_values

	def defuzzificate(self, out_fuzzy_values):
		"""Returns crisp values, mapped to out_variables"""
		result = {}
		for v in self.out_variables.values():
			result[v.name] = out_fuzzy_values[v.name].get_center_of_mass_fast()

		return result

	def process(self, in_crisp_values):
		in_fuzzy_values = self.fuzzificate(in_crisp_values)
		# print(list(str(v) for v in in_fuzzy_values.values()))
		out_fuzzy_values = self.apply_rules(in_fuzzy_values)
		# print(list(str(v) for v in out_fuzzy_values.values()))
		out_crisp_values = self.defuzzificate(out_fuzzy_values)

		return out_crisp_values


if __name__ == '__main__':
	inf = float(math.inf)

	As = Term('As', 0, 0, 3, 5)
	Al = Term('Al', 3, 6, inf, inf)
	A = Variable('A', [As, Al], 0, 10)

	Bs = Term('Bs', 0, 0, 3, 6)
	Bl = Term('Bl', 4, 6, inf, inf)
	B = Variable('B', [Bs, Bl], 0, 10)

	Ws = Term('Ws', 0, 0, 1, 3)
	Wm = Term('Wm', 2, 4, 6, 8)
	Wl = Term('Wl', 6, 9, inf, inf)
	W = Variable('W', [Ws, Wm, Wl], 0, 10)

	in_variables = [A, B]

	out_variables = [W, ]

	rules = [
		Rule([Cond(A, As), Cond(B, Bs)], [Cond(W, Ws)]),
		Rule([Cond(A, As), Cond(B, Bl)], [Cond(W, Wm)]),
		Rule([Cond(A, Al), Cond(B, Bs)], [Cond(W, Wm)]),
		Rule([Cond(A, Al), Cond(B, Bl)], [Cond(W, Wl)]),
	]

	in_crisp_values = {'A': 4, 'B': 5}

	alg = MamdaniAlgorithm(in_variables, out_variables, rules)

	in_fuzzy_values = alg.fuzzificate(in_crisp_values)
	print(list(str(v) for v in in_fuzzy_values.values()))
	# ["FuzzyValue(A, 4.00, ['As(0.50)', 'Al(0.33)'])", "FuzzyValue(B, 5.00, ['Bs(0.33)', 'Bl(0.50)'])"]

	out_fuzzy_values = alg.apply_rules(in_fuzzy_values)
	print(list(str(v) for v in out_fuzzy_values.values()))
	# ["FuzzyValue(W, 0.00, ['Wl(0.33)', 'Wm(0.50)', 'Ws(0.33)'])"]

	start = time.time()
	out_crisp_values = alg.defuzzificate(out_fuzzy_values)
	print(out_crisp_values)
	#{'W': 5.0}
	print(time.time() - start)

# alg.process(in_crisp_values)
