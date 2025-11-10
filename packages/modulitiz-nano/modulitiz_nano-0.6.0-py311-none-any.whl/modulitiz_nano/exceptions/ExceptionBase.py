from modulitiz_nano.exceptions.ExceptionRuntime import ExceptionRuntime


class ExceptionBase(ExceptionRuntime):
	
	def __init__(self,*args):
		super().__init__(*args)
