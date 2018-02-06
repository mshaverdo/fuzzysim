import math

applying_a = 0
time_quantum = 0.001


def get_a(current_s, current_v, current_a):
	global applying_a

	target_a = (-2 * current_v ** 2 / (3 * current_s))
	j = abs(current_v ** 3 / current_s ** 2)
	j = math.copysign(j, target_a - current_a)
	applying_a += j * time_quantum

	return applying_a
