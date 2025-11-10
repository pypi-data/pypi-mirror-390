from modulitiz_nano.util.spooler.exceptions.ExceptionSpooler import ExceptionSpooler


class ExceptionSpoolerFull(ExceptionSpooler):
	
	def __init__(self):
		super().__init__("Spooler pieno")
