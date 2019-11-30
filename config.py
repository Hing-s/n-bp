class Config:
	def __init__(self, config):
		for i in config:
			setattr(self, i, config[i])
