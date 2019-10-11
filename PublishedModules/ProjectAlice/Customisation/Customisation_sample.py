from core.base.model.Module import Module


class Customisation(Module):
	"""
		You can use this class to override anything any module do. Want something happening when you are going bed? Override onGoingBed!
	"""
	MODULE_NAME = 'Customisation'


	def __init__(self):
		self._SUPPORTED_INTENTS = list()

		super().__init__(self._SUPPORTED_INTENTS)