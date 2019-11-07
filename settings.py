import numpy as np

POPULATION_AGENT_CLASS = 'population'
PROPAGANDA_AGENT_CLASS = 'propaganda'
COP_AGENT_CLASS = 'cop'
TRANSFER_STRATEGY = 0
BANDWAGON_STRATEGY = 1
DEMONIZING_STRATEGY = 2

def tuned_sigmoid(z, alpha=1, clip=1):
	return 1 / (1 + np.exp( - alpha * ( 12/(1+clip)*z-6 )))
