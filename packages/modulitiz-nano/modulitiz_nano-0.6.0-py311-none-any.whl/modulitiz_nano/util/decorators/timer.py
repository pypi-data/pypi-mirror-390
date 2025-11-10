import time
from functools import wraps


def timer(func):
	"""
	Measure execution time of function.
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		result = func(*args, **kwargs)
		duration = time.perf_counter() - start
		wrapper.lastTime = duration
		wrapper.totalTime += duration
		return result
	wrapper.lastTime = 0
	wrapper.totalTime = 0
	return wrapper
