from mesa import Agent, Model


class PopulationAgent(Agent):
    """An agent that can become active."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class CopAgent(Agent):
    """An agent that can arrest PopulationAgents."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)