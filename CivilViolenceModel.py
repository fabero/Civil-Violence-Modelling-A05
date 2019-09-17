from mesa import Agent, Model
from mesa.time import RandomActivation

class PopulationAgent(Agent):
    """An agent that can become active."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

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

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()