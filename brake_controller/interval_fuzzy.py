import math
from mamdani import IntervalTerm, Term, Variable, Rule, Cond, MamdaniAlgorithm


class Controller:
	def __init__(self):
		inf = float(math.inf)

		# S_sch[min, S-small peak, S-large peak, max]
		# V_sch[min, V-small peak, V-large peak, max]
		#A_schema[min, A-small peak, A-mid peak, A-large peak, max]

		# experiment nuber 2
		S_sch = [0, 25, 75, 100]
		V_sch = [0, 5, 15, 20]
		A_sch = [0, 5.47]

		Ss = Term('Ss', S_sch[0], S_sch[0], S_sch[1], S_sch[2])
		Sl = Term('Sl', S_sch[1], S_sch[2], inf, inf)
		S = Variable('S', [Ss, Sl], S_sch[0], S_sch[3])

		Vs = Term('Vs', V_sch[0], V_sch[0], V_sch[1], V_sch[2])
		Vl = Term('Vl', V_sch[1], V_sch[2], inf, inf)
		V = Variable('V', [Vs, Vl], V_sch[0], V_sch[3])

		a_min = A_sch[0]
		a_max = A_sch[len(A_sch)-1]

		# very rude
		A_terms = [0] * 2
		A_terms[0] = IntervalTerm('A0', a_min, (a_max+a_min)/2)
		A_terms[1] = IntervalTerm('A1', (a_max+a_min)/2, a_max)
		A = Variable('A', A_terms, a_min, a_max)

		in_variables = [S, V]

		out_variables = [A, ]

		#very rude
		rules = [
			Rule([Cond(S, Ss), Cond(V, Vs)], [Cond(A, A_terms[0])]),
			Rule([Cond(S, Ss), Cond(V, Vl)], [Cond(A, A_terms[1])]),
			Rule([Cond(S, Sl), Cond(V, Vs)], [Cond(A, A_terms[0])]),
			Rule([Cond(S, Sl), Cond(V, Vl)], [Cond(A, A_terms[0])]),
		]

		self.alg = MamdaniAlgorithm(in_variables, out_variables, rules)

	def get_a(self, current_s, current_v):
		out = self.alg.process({'S': current_s, 'V': current_v})
		return -out['A']


default_controller = Controller()


def get_a(current_s, current_v, current_a):
	current_v = max(current_v, 0)
	current_s = max(current_s, 0)

	if current_v == 0:
		return 0
	a = default_controller.get_a(current_s, current_v)
	# print(current_s, current_v, a)
	return a
