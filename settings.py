import numpy as np

POPULATION_AGENT_CLASS = 'population'
PROPAGANDA_AGENT_CLASS = 'propaganda'
COP_AGENT_CLASS = 'cop'

def tuned_sigmoid(z, alpha=1, clip=1):
	return 1 / (1 + np.exp( - alpha * ( 12/(1+clip)*z-6 )))
