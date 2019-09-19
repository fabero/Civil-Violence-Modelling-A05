from mesa import Agent


class CopAgent(Agent):
    """An agent that can arrest PopulationAgents."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # The agent's step will go here.
        pass
