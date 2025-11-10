import asyncio
from functools import wraps
from typing import Coroutine

import nest_asyncio


def noAwait(func):
	"""
	Usare questo decorator per evitare di propagare async e await in tutto il codice.
	Esempio dell'uso:

	@noAwait
	async def funzione(self):
		await funzioneAsync()
	"""
	
	@wraps(func)
	def wrapped(*args, **kwargs):
		try:
			loop=asyncio.get_event_loop_policy().get_event_loop()
		except RuntimeError:
			loop=asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		nest_asyncio.apply(loop)
		coroutine:Coroutine=func(*args,**kwargs)
		task=loop.create_task(coroutine)
		return loop.run_until_complete(task)
	return wrapped
