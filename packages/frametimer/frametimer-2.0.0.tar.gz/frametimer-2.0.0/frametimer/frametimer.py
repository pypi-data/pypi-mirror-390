import sys
import time

class FrameTimer:
	"""
	An accurate periodic timer. Given an FPS or delay value, does its best to make sure calls to `tick` are exactly that much apart.
	"""

	target_delay: float
	spin_time: float
	last_tick_time: None | float

	def __init__(self, fps: int | float | None = 60, delay: float | None = None, *, spin_time: float | None = None):
		"""
		Creates a FrameTimer given given an 'fps' (frames or ticks per second, FPS) or 'delay' (delay between two frames or ticks) value.
		Defaults to 60 FPS or 0.01(6) seconds of delay.
		"""
		if delay is not None:
			self.target_delay = delay
		elif fps is not None:
			self.target_delay = 1.0 / fps
		else:
			raise TypeError("One of 'fps' or 'delay' must be specified")

		if spin_time is None:
			self.spin_time = self._guess_spin_time()
		else:
			self.spin_time = spin_time
		self.last_tick_time = None

	def _guess_spin_time(self) -> float:
		if sys.platform.startswith('linux'):
			return 0.001
		else:
			return 0.01

	def tick(self, delay: float | None = None) -> float:
		"""
		Starts or advances the timer. Waits until it's time for the next frame and returns the time passed since the last frame.
		This method should be called at the start of every frame. The return value can be used for framerate-independent calculations.
		Returns 0 the first time it's called.
		"""
		if delay is None:
			delay = self.target_delay

		if self.last_tick_time is None:
			self.last_tick_time = self.now()
			return 0.0

		self.accurate_sleep_until(self.last_tick_time + delay)

		now = self.now()
		dt = now - self.last_tick_time
		self.last_tick_time = now
		return dt

	def accurate_sleep_until(self, target_time: float):
		"""
		Sleeps accurately until the specified time
		"""
		sleep_time = target_time - self.now() - self.spin_time
		if sleep_time > 0:
			self.sleep(sleep_time)

		while self.now() < target_time:
			pass

	def accurate_sleep(self, delay: float):
		"""
		Sleeps accurately for the given number of seconds
		"""
		self.accurate_sleep_until(self.now() + delay)

	def sleep(self, seconds: float):
		"""
		The base sleep function of the FrameTimer, sleeps for the given amount of seconds.
		Can be overridden, to use another sleep function.
		"""
		time.sleep(seconds)

	def now(self) -> float:
		"""
		The base timer of the FrameTimer, returns the current time in seconds.
		Can be overridden, to use another timer.
		"""
		return time.perf_counter()
