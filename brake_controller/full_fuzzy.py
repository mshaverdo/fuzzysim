import math
from mamdani import Term, Variable, Rule, Cond, MamdaniAlgorithm


class Controller:
	def __init__(self):
		inf = float(math.inf)

		# S_sch[min, S-small peak, S-large peak, max]
		# V_sch[min, V-small peak, V-large peak, max]
		#A_schema[min, A-small peak, A-mid peak, A-large peak, max]

		# experiment nuber 0
		# S_sch = [0, 0, 200, 200]
		# V_sch = [0, 0, 40, 40]
		# A_sch = [0, 0, 5, 10, 10]

		# experiment nuber 1
		# S_sch = [0, 0, 100, 100]
		# V_sch = [0, 0, 20, 20]
		# A_sch = [0, 0, 5, 10, 10]

		# experiment nuber 2
		S_sch = [0, 25, 75, 100]
		V_sch = [0, 5, 15, 20]
		A_sch = [0, 0, 5, 10, 10]

		# experiment nuber 3
		S_sch = [0, 50, 50, 100]
		V_sch = [0, 10, 10, 20]
		A_sch = [0, 0, 5, 10, 10]



		Ss = Term('Ss', S_sch[0], S_sch[0], S_sch[1], S_sch[2])
		Sl = Term('Sl', S_sch[1], S_sch[2], inf, inf)
		S = Variable('S', [Ss, Sl], S_sch[0], S_sch[3])

		Vs = Term('Vs', V_sch[0], V_sch[0], V_sch[1], V_sch[2])
		Vl = Term('Vl', V_sch[1], V_sch[2], inf, inf)
		V = Variable('V', [Vs, Vl], V_sch[0], V_sch[3])

		As = Term('As', A_sch[0], A_sch[0], A_sch[1], A_sch[2])
		Am = Term('Am', A_sch[1], A_sch[2], A_sch[2], A_sch[3])
		Al = Term('Am', A_sch[2], A_sch[3], inf, inf)
		A = Variable('A', [As, Am, Al], A_sch[0], A_sch[4])



		# Ss = Term('Ss', 0, 0, 0, 100)
		# Sl = Term('Sl', 0, 100, inf, inf)
		# S = Variable('S', [Ss, Sl], 0, 110)
		#
		# Vs = Term('Vs', 0, 0, 0, 30)
		# Vl = Term('Vl', 0, 30, inf, inf)
		# V = Variable('V', [Vs, Vl], 0, 20)
		#
		As = Term('As', 0, 0, 0, 5)
		Am = Term('Am', 0, 5, 5, 10)
		Al = Term('Al', 5, 10, inf, inf)
		A = Variable('A', [As, Am, Al], 0, 10)




		# Ss = Term('Ss', 0, 0, 200, 300)
		# Sl = Term('Sl', 200, 300, inf, inf)
		# S = Variable('S', [Ss, Sl], 0, 500)
		#
		# Vs = Term('Vs', 0, 0, 20, 30)
		# Vl = Term('Vl', 20, 30, inf, inf)
		# V = Variable('V', [Vs, Vl], 0, 50)
		#
		# As = Term('As', 0, 0, 5, 10)
		# Am = Term('Am', 5, 10, 20, 25)
		# Al = Term('Al', 20, 25, inf, inf)
		# A = Variable('A', [As, Am, Al], 0, 30)

		in_variables = [S, V]

		out_variables = [A, ]

		rules = [
			Rule([Cond(S, Ss), Cond(V, Vs)], [Cond(A, As)]),
			Rule([Cond(S, Ss), Cond(V, Vl)], [Cond(A, Al)]),
			Rule([Cond(S, Sl), Cond(V, Vs)], [Cond(A, As)]),
			Rule([Cond(S, Sl), Cond(V, Vl)], [Cond(A, As)]),
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
