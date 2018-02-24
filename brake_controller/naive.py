import math

applying_a = 0
time_quantum = 0.001
search_j = None
current_j = None
const_a = None


def get_a(current_s, current_v, current_a):
	global applying_a, search_j, current_j, const_a
	if search_j is None:
		const_a = -current_v ** 2 / (2 * current_s)
		time_a_const = 2 * current_s / current_v
		search_j = abs((const_a - current_a) * 2 / (time_a_const / 2))
		current_j = -search_j

	if current_j == -search_j:
		current_j = math.copysign(search_j, const_a*2 - applying_a)

	applying_a += current_j * time_quantum
	return applying_a
