import math
from mamdani import Term, Variable, Rule, Cond, MamdaniAlgorithm

time_quantum = 0.001


class Controller:
	def __init__(self):
		inf = float(math.inf)

		Ss = Term('Ss', 0, 0, 0, 75)
		Sl = Term('Sl', 25, 100, inf, inf)
		S = Variable('S', [Ss, Sl], 0, 100)

		Vs = Term('Vs', 0, 0, 0, 15)
		Vl = Term('Vl', 5, 20, inf, inf)
		V = Variable('V', [Vs, Vl], 0, 20)

		As = Term('As', 0, 0, 0, 12)
		Al = Term('Al', 4, 15, inf, inf)
		A = Variable('A', [As, Al], 0, 15)

		J0 = Term('J0', 0, 0, 0, 0.25)
		J025 = Term('J025', 0, 0.25, 0.25, 7)
		J7 = Term('J7', 0.25, 7, 7, 25)
		J25 = Term('J25', 7, 25, 25, 100)
		J100 = Term('J100', 25, 100, 100, inf)
		J = Variable('J', [J0, J025, J7, J25, J100], 0, 100)
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

		in_variables = [S, V, A]

		out_variables = [J, ]

		rules = [
			Rule([Cond(S, Ss), Cond(V, Vs), Cond(A, As)], [Cond(J, J025)]), #as = 0 (target_a == a == 0.6), Js= 0.25
			Rule([Cond(S, Ss), Cond(V, Vs), Cond(A, Al)], [Cond(J, J100)]), #al = 15 (target_a ==0.6 a == 15.6), Jxl= 100
			Rule([Cond(S, Ss), Cond(V, Vl), Cond(A, As)], [Cond(J, J7)]), #As = 0 (дельта a_target == a == 15), потребный рывок jm=6
			Rule([Cond(S, Ss), Cond(V, Vl), Cond(A, Al)], [Cond(J, J25)]), #Al = 15 (дельта a_target == 15, a = 0), потребный рывок jl=25
			Rule([Cond(S, Sl), Cond(V, Vs), Cond(A, As)], [Cond(J, J0)]), #As = 0 (a_target == a == 0.01), потребный рывок jxs=0.001
			Rule([Cond(S, Sl), Cond(V, Vs), Cond(A, Al)], [Cond(J, J100)]), #al = 15 (target_a ==0.01 a == 15), Jxl= 100
			Rule([Cond(S, Sl), Cond(V, Vl), Cond(A, As)], [Cond(J, J025)]), #as = 0 (target_a == a == 2.5), Js= 0.25
			Rule([Cond(S, Sl), Cond(V, Vl), Cond(A, Al)], [Cond(J, J7)]), #al = 15 (target_a ==2.5 a == 17.5), Jm= 8.5
		]

		self.alg = MamdaniAlgorithm(in_variables, out_variables, rules)

	def get_a(self, current_s, current_v, current_a):
		current_v = max(current_v, 0)
		current_s = max(current_s, 0)

		if current_v == 0:
			return 0
		target_a = (-2 * current_v ** 2 / (3 * current_s))

		out = self.alg.process({'S': current_s, 'V': current_v, 'A': abs(target_a - current_a)})
		j = out['J']

		j = math.copysign(j, target_a - current_a)

		a = current_a + j * time_quantum
		return a


default_controller = Controller()


def get_a(current_s, current_v, current_a):
	# print(current_s, current_v, current_a)
	a = default_controller.get_a(current_s, current_v, current_a)
	return a
