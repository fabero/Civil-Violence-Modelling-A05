from mesa import Agent, Model
from mesa.time import RandomActivation


class PopulationAgent(Agent):
    """An agent that can become active."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.hardship = 0
        self.legitimacy = 0
        self.grievance = 0
        self.active = False
        self.risk_aversion = 0

    def step(self):
        # The agent's step will go here.
        pass


class CopAgent(Agent):
    """An agent that can arrest PopulationAgents."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # The agent's step will go here.
        pass


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