from modulitiz_nano.exceptions.ExceptionBase import ExceptionBase


class ExceptionSpooler(ExceptionBase):
	
	def __init__(self,msg:str):
		super().__init__(msg)
