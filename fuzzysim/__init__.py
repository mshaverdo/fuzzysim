import math

class CartController:
	time_quantum = 0.001  # time quantum in seconds

	def __init__(self, physics, brake_controller, brake_distance):
		"""
		Init controller

		:param physics:				reference to environment
		:param brake_distance: 	distance, when brake begins, m
		"""
		brake_controller.time_quantum = self.time_quantum

		self._physics = physics
		self._brake_controller = brake_controller
		self._brake_distance = brake_distance

	def tick(self):
		"""
		process controller tick
		"""
		(s, v, a) = self._physics.get_controller_params()

		applying_a = self._brake_controller.get_a(s, v, a)
		self._physics.apply_acceleration(applying_a)


class WayConfig:
	def __init__(self):
		self._obstacles = list()

	def get_effective_a(self, s, a):
		for o in self._obstacles:
			a = o.get_effective_a(s, a)

		return a


class Obstacle:
	def __init__(self, start, end, delta_a=None, max_a=None):
		if start > end:
			(start, end) = (end, start)

		self.start = start
		self.end = end
		self.max_a = max_a if max_a is not None else 100000
		self.delta_a = delta_a if delta_a is not None else 0

	def get_effective_a(self, s, a):
		if not self.start < s < self.end:
			return a

		a = math.copysign(min(abs(a), self.max_a), a)
		a += self.delta_a

		return a


class CollisionError(RuntimeError):
	def __init__(self, t, s, v, a):
		self.t = t
		self.s = s
		self.v = v
		self.a = a

	def __str__(self):
		return "Collision happens: T=%.3f S=%.3f V=%.3f A=%.3f" % (self.t, self.s, self.v, self.a)


class PhysModel:
	time_quantum = 0.001  # seconds
	speed_zero = 0.001  # assume platform stopped if it;s speed <= speed_zero

	def __init__(self, s0, v0, way_config, acceleration_lag=0):
		"""
		:param v0: m/s		initial speed
		:param s0: m		initial distance
		:param way_config:  way configuration
		:param acceleration_lag:  acceleration latency in seconds
		"""

		self._v = v0  # m/s
		self._s = s0  # m
		self._a = 0
		self._t = 0
		self._way_config = way_config
		self._a_queue = []
		self._acceleration_lag = acceleration_lag

	def apply_acceleration(self, a):
		"""
		Set current acceleration value by controller

		:param a: 	target acceleration, m/s^2
		:return:
		"""
		appliance_time = self._t + self._acceleration_lag

		self._a_queue.append((appliance_time, a))

	def get_params(self):
		"""
		Return current cart params

		:return: 	(t, s, v, a)
		"""

		return self._t, self._s, self._v, self._a

	def get_controller_params(self):
		"""
		Return current distance, speed and acceleration to controller

		:return:	s, v, a
		"""
		return self._s, self._v, self._a

	def is_stopped(self):
		"""
		return true if platform stopped

		:return:
		"""

		return self._v <= self.speed_zero

	def tick(self):
		"""
		process tick

		:return: True if platform stopped in this quant
		"""
		self._t += self.time_quantum

		# apply a from queue
		for i, v in enumerate(self._a_queue):
			if v[0] <= self._t:
				self._a = v[1]
				del self._a_queue[i]

		self._a = self._way_config.get_effective_a(self._s, self._a)

		self._v += self._a * self.time_quantum
		self._s -= self._v * self.time_quantum + (self._a * self.time_quantum ** 2) / 2

		if self._s <= 0 and not self.is_stopped():
			raise CollisionError(self._t, self._s, self._v, self._a)

		# if distance less then 1 quantum zero speed distance, assume it is 0
		if abs(self._s) < self.time_quantum * self.speed_zero:
			self._s = 0


class Simulator:
	"""
	Manage controllers, generate ticks, collects stats
	"""
	time_quantum = 0.001
	j_stats_limit = 100

	def __init__(self, physics, controller):
		"""
		Inits world

		:param physics: PhysModel
		:param controller: CartController
		"""
		physics.time_quantum = self.time_quantum
		controller.time_quantum = self.time_quantum

		self._physics = physics
		self._controller = controller

		self.stats_t = []
		self.stats_s = []
		self.stats_v = []
		self.stats_a = []
		self.stats_j = []

	def start(self):
		"""
		Start simulation and loop ticks until platform stops or crashes

		:return: True if stop is ok, false if crash occurs
		"""
		prev_a = 0
		while not self._physics.is_stopped():
			try :
				self._physics.tick()
			except CollisionError as e:
				return False, e.t, e.s, e.v, e.a

			self._controller.tick()

			(t, s, v, a) = self._physics.get_params()

			# calculate jerk for current model time moment as da/dt:
			j = (a - prev_a) / (self.time_quantum)
			j = math.copysign(min(abs(j), self.j_stats_limit), j)
			prev_a = a

			self.stats_t.append(t)
			self.stats_s.append(s)
			self.stats_v.append(v)
			self.stats_a.append(a)
			self.stats_j.append(j)


		return True, t, s, v, a
