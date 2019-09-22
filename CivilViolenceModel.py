from mesa import Model
from mesa.time import RandomActivation
from PopulationAgent import PopulationAgent
from CopAgent import CopAgent

class CivilViolenceModel(Model):
    """A model with some number of PopulationAgents and some number of CopAgents."""
    def __init__(self, nPopulation, nCops):
        self.num_population = nPopulation
        self.num_cops = nCops
        self.max_jail_term = 0
        self.schedule = RandomActivation(self)
        # Create PopulationAgents
        for i in range(self.num_population):
            a = PopulationAgent(i, self)
            self.schedule.add(a)
        # Create CopAgents
        for i in range(self.num_cops):
            b = CopAgent(i, self)
            self.schedule.add(b)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
