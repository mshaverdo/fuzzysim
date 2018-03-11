import math
from scipy.integrate import quad
import time
import numpy


# Предложение: использовать термы не интервальные, а прямоугольные: задавать им максивмальную высоту:
# это должно сильно улучшить точность и упростить генерацию правил: мы можем аппроксимировать боковые
# участки трапеций такими термами с высотой менее единицы

class RectangleTerm():
	def __init__(self, name, a, d, height):
		self.name = name
		self.a = a
		self.b = a
		self.c = d
		self.d = d
		self.height = height
		self.width = abs(a - d)

		if self.width > 10e100:
			raise ValueError("RectangleTerm width can't be infinite")

	def degree(self, crisp_value):
		if self.a <= crisp_value <= self.d:
			return self.height
		else:
			return 0


class IntervalTerm(RectangleTerm):
	def __init__(self, name, a, d):
		super().__init__(name, a, d, 1)


class Term:
	def __init__(self, name, a, b, c, d):
		self.name = name
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.height = 1

	def degree(self, crisp_value):
		if self.a < crisp_value < self.b:
			return (crisp_value - self.a) / (self.b - self.a)
		elif self.b <= crisp_value <= self.c:
			return 1
		elif self.c < crisp_value < self.d:
			return (self.d - crisp_value) / (self.d - self.c)
		else:
			return 0


class Variable:
	def __init__(self, name, terms, min, max):
		self.name = name
		self.terms = {v.name: v for v in list(terms)}
		self.min = min
		self.max = max

	def get_fuzzy_value(self, crisp_value=None):
		"""

		:param crisp_value:
		:return: FuzzyValue
		"""
		if crisp_value is None:
			term = list(self.terms.values())[0]
			if type(term) is IntervalTerm:
				return IntervalFuzzyValue(self, crisp_value, {})
			elif type(term) is RectangleTerm:
				return RectangleFuzzyValue(self, crisp_value, {})
			else:
				return FuzzyValue(self, None, {})

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
		return "%s(%s, %.2f, %s)" % (
			type(self),
			self.variable.name,
			self.precise_value or 0,
			list(str(v) for v in self.memberships.values())
		)

	def get_membership(self, term):
		if term.name not in self.memberships:
			raise RuntimeError("%s : %s" % (self, term))
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
			result += self.degree(x) * delta
			if upto is not None and result > upto:
				return result, x

		return result

	def get_center_of_mass(self):
		weight = self.integrate()
		if weight == 0:
			return 0
		_, center_x = self.integrate(weight / 2)
		return center_x


class IntervalFuzzyValue(FuzzyValue):
	"""
	Термы выходной переменной должны быть
	- заданы на непрерывном интервале,
	- должны быть отсортированы в порядке следования по области определения
	"""

	def __init__(self, variable, precise_value, memberships):
		super().__init__(variable, precise_value, memberships)
		self.sorted_memberships = sorted(memberships.values(), key=lambda x: x.term.a)

	def add_membership(self, membership, unite=True):
		super().add_membership(membership, unite)
		self.sorted_memberships = sorted(self.memberships.values(), key=lambda x: x.term.a)

	def get_membership_mass(self, membership):
		return  membership.term.width * membership.degree

	def get_center_of_mass(self):
		masses = [0] * len(self.sorted_memberships)
		total_mass = 0
		for i, m in enumerate(self.sorted_memberships):
			masses[i] = self.get_membership_mass(m)
			total_mass += masses[i]

		if total_mass == 0:
			return (self.variable.max + self.variable.min)/2

		half_mass = total_mass / 2
		center = 0
		for i, v in enumerate(masses):
			half_mass -= v
			if half_mass <= 0:
				ratio = 1 - abs(half_mass / v)
				center += ratio * self.sorted_memberships[i].term.width
				return center

			center += self.sorted_memberships[i].term.width


class RectangleFuzzyValue(IntervalFuzzyValue):
	def get_membership_mass(self, membership):
		return membership.term.width * min(membership.degree, membership.term.height)


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
			aggregated_degree = min(memberships).degree

			for c in r.conclusions:
				if c.variable.name not in out_fuzzy_values:
					out_fuzzy_values[c.variable.name] = c.variable.get_fuzzy_value(None)

				out_fuzzy_values[c.variable.name].add_membership(Membership(c.term, aggregated_degree))

		return out_fuzzy_values

	def defuzzificate(self, out_fuzzy_values):
		"""Returns crisp values, mapped to out_variables"""
		result = {}
		for v in self.out_variables.values():
			result[v.name] = out_fuzzy_values[v.name].get_center_of_mass()

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
	Wl = Term('Wl', 6, 8, inf, inf)
	W = Variable('W', [Ws, Wm, Wl], 0, 10)

	#to test speed
	# Ws = RectangleTerm('Ws', 0, 2, 1)
	# Wsm = RectangleTerm('Ws', 2, 3, 0.5)
	# Wm = RectangleTerm('Ws', 3, 6.5, 1)
	# Wml = RectangleTerm('Ws', 6.5, 7.5, 0.5)
	# Wl = RectangleTerm('Wl', 7.5, 10, 1)
	# W = Variable('W', [Ws, Wsm, Wm, Wml, Wl], 0, 10)

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

	out_crisp_values = alg.defuzzificate(out_fuzzy_values)
	print(out_crisp_values)
	# {'W': 5.0}

	# test interval fuzzy value
	# use 3x ratio for traditional fuzzy terms to approximate trapezoid terms:
	# 2 interval terms for leg parts of trapezod term and 1 for base part
	# so, in this benchmark we use 9 intervalTerms to approximate output var W with 3 trapezoid terms
	Its = [
		IntervalTerm('I0', 0, 0.5),
		IntervalTerm('I1', 0.5, 1),
		IntervalTerm('I2', 1, 2.5),
		IntervalTerm('I3', 2.5, 4),
		IntervalTerm('I4', 4, 6),
		IntervalTerm('I5', 6, 7.2),
		IntervalTerm('I6', 7.2, 9),
		IntervalTerm('I7', 9, 9.5),
		IntervalTerm('I8', 9.5, 10),
	]
	I = Variable('I', Its, 0, 10)

	degrees = [1, 1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, ]
	Imemberships = {"I%d" % i: Membership(Its[i], v) for i, v in enumerate(degrees)}
	ifv = IntervalFuzzyValue(I, None, Imemberships)

	center = ifv.get_center_of_mass()
	# center == 4.666666666666666
	print("Interval center", center)

	# test rectangle fuzzy value
	# use 3x ratio for traditional fuzzy terms to approximate trapezoid terms:
	# 2 interval terms for leg parts of trapezoid term and 1 for base part
	# so, in this benchmark we use 9 intervalTerms to approximate output var W with 3 trapezoid terms
	Rts = [
		RectangleTerm('R0', 0, 0.5, 0.6),
		RectangleTerm('R1', 0.5, 1, 0.6),
		RectangleTerm('R2', 1, 2.5, 0.6),
		RectangleTerm('R3', 2.5, 4, 0.6),
		RectangleTerm('R4', 4, 6, 1),
		RectangleTerm('R5', 6, 7.2, 0.6),
		RectangleTerm('R6', 7.2, 9, 0.6),
		RectangleTerm('R7', 9, 9.5, 1),
		RectangleTerm('R8', 9.5, 10, 1),
	]
	R = Variable('R', Rts, 0, 10)

	degrees = [1, 1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, ]
	Rmemberships = {"R%d" % i: Membership(Rts[i], v) for i, v in enumerate(degrees)}
	rfv = RectangleFuzzyValue(R, None, Rmemberships)

	center = rfv.get_center_of_mass()
	# center == 5.0
	print("Rectangle center", center)

	# benchmark
	iterations = 10000
	start = time.time()
	for i in range(0, iterations):
		in_fuzzy_values = alg.fuzzificate(in_crisp_values)
	print("%d alg.fuzzificate takes %.1f ms" % (iterations, 1000 * (time.time() - start)))

	start = time.time()
	for i in range(0, iterations):
		out_fuzzy_values = alg.apply_rules(in_fuzzy_values)
	print("%d alg.apply_rules takes %.1f ms" % (iterations, 1000 * (time.time() - start)))

	start = time.time()
	for i in range(0, iterations):
		out_crisp_values = alg.defuzzificate(out_fuzzy_values)
	print("%d alg.defuzzificate takes %.1f ms" % (iterations, 1000 * (time.time() - start)))

	start = time.time()
	for i in range(0, iterations):
		center = ifv.get_center_of_mass()
	print("%d ifv.get_center_of_mass takes %.1f ms" % (iterations, 1000 * (time.time() - start)))

	start = time.time()
	for i in range(0, iterations):
		center = rfv.get_center_of_mass()
	print("%d rfv.get_center_of_mass takes %.1f ms" % (iterations, 1000 * (time.time() - start)))

# alg.process(in_crisp_values)
