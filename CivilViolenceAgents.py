import math

from mesa import Agent


class PopulationAgent(Agent):
    '''
    An agent from the population distribution, can become active and be jailed
    Movement Rule: Move to a random empty cell within local vision
    Activation Rule: If Grievance - NetRisk > Threshold go active

    Attributes:
    unique_id: a unique id
    hardship: Perceived hardship (e.g economic privation). Drawn from U(0,1)
    legitimacy: Global perception of the regime's legitimacy. Exogenous.
    risk_aversion: Potential for taking risks. Drawn from U(0,1)
    threshold: how much must Grievance > NetRisk in order to go active
    vision: number of patches in all 4 directions inside agent's inspection.
    pos: (x,y) grid coordinates

    '''

    def __init__(
            self,
            unique_id,
            model,
            hardship,
            legitimacy,
            risk_aversion,
            threshold,
            vision,
            pos):
        '''
        Initiate a PopulationAgent

        Args:
        unique_id: a unique id
        hardship: Perceived hardship (e.g economic privation). Drawn from U(0,1)
        legitimacy: Global perception of the regime's legitimacy. Exogenous.
        grievance: Agent grievance parameter
        active: Agent current rebellion status (True for Active / False for Quiescent)
        risk_aversion: Potential for taking risks. Drawn from U(0,1)
        threshold: How much must Grievance > NetRisk in order to go active
        vision: Number of patches in all 4 directions inside cop's inspection.
        arrest_probability: Perceived likelihood of arrest
        jail_time: Number of steps remaining in jail, if arrested
        pos: (x,y) grid coordinates
        model: model instance
        '''

        super().__init__(unique_id, model)
        self.agent_class = 'population'
        self.hardship = hardship
        self.legitimacy = legitimacy
        self.grievance = self.hardship * (1 - self.legitimacy)
        self.active = False
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.vision = vision
        self.jail_time = 0
        self.arrest_probability = None
        self.pos = pos

    def step(self):
        # The population agent's movement and activenes rules A and M from the
        # paper
        """
            If an agent is jailed it cannot move in the grid
            For each step, their jail time will be reduced by 1
            If a jailed agent is released, they are inactive
        """

        if self.jail_time:
            self.jail_time -= 1
            if not self.jail_time:
                self.active = False
            return

        """
            Get information of the neighborhood.
            Get all the neighbors info and empty cells in neighborhood
        """

        # position of neighborhood cells
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=self.vision)
        # attributes of all the neighboars
        self.neighbors = self.model.grid.get_cell_list_contents(
            self.neighborhood)
        # empty neighborhood cells
        self.empty_cells = [
            cell for cell in self.neighborhood if self.model.grid.is_cell_empty(cell)]

        """
            Get arrest probability based on number of active agents
            to cop ratio in the neighborhood
        """

        cops_in_vision = len(
            [agent for agent in self.neighbors if agent.agent_class == "cop"])

        # agent counts herself as active when estimating arrest probability
        actives_in_vision = 1
        for agent in self.neighbors:
            if agent.agent_class == "population" and agent.active and not agent.jail_time:
                actives_in_vision += 1

        # defining arrest probability for each agent
        # depending on cop-to-active ratio
        # arrest_prob _constant is defined as 2.3 in the netlogo implementation
        # a rounding to min integer is implemented as suggested in the netlogo
        # implementation
        self.ratio_c_a = int(cops_in_vision / actives_in_vision)
        self.arrest_probability = (
            1 - math.exp(-1 * self.model.arrest_prob_constant * self.ratio_c_a))

        # calculating net_risk given risk aversion and arrest probability
        # we further calculate a bool value if difference of grievance and net_risk
        # is greater than threshold value which is defined as 0.1 in net logo
        # implementation
        self.net_risk = self.risk_aversion * self.arrest_probability
        thresh_bool = (self.grievance - self.net_risk) > self.threshold

        # simple state transition rule A for population agent
        # Case 1: if state is inactive and thresh bool is true
        # then transition to an active state, set active flag to true
        # Case 2: if active flag is true but thresh bool has changed to false
        # then transition back to inactive state
        if not self.active and thresh_bool:
            self.active = True
        elif self.active and not thresh_bool:
            self.active = False

        # randomly move to an empty neighborhood cell
        if self.model.movement and self.empty_cells:
            new_pos = self.random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)


class CopAgent(Agent):
    """
    An agent that can arrest PopulationAgents.
    Movement Rule: Arrest an active agent in local vision. Move to her position

    Attributes:
        unique_id: a unique id
        vision: number of patches in all 4 directions inside cop's inspection.
        pos: (x,y) grid coordinates
    """

    def __init__(self, unique_id, model, vision, pos):
        '''
        Initiate a CopAgent
        Args:
        unique_id: a unique id
        vision: number of patches in all 4 directions inside cop's inspection.
        pos: (x,y) grid coordinates
        model: model instance
        '''
        super().__init__(unique_id, model)
        self.agent_class = 'cop'
        self.vision = vision
        self.pos = pos

    def step(self):
        # The cop's movement rule M from the paper
        """
            Get information of the neighborhood.
            Get all the neighbors info and empty cells in neighborhood
        """

        # position of neighborhood cells
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=self.vision)
        # attributes of all the neighboars
        self.neighbors = self.model.grid.get_cell_list_contents(
            self.neighborhood)
        # empty neighborhood cells
        self.empty_cells = [
            cell for cell in self.neighborhood if self.model.grid.is_cell_empty(cell)]

        # find the number of active agents in neighborhood
        actives = []
        for agent in self.neighbors:
            if agent.agent_class == 'population' and agent.active and not agent.jail_time:
                actives.append(agent)

        # arrest a random active agent and jail her for a random choice of up
        # to JAIL_MAX_TERM steps
        if actives:
            jailed = self.random.choice(actives)
            jailed.jail_time = self.random.randint(0, self.model.max_jail_term)
            if self.model.movement:
                self.model.grid.move_agent(self, jailed.pos)

        # otherwise move if applicable to an empty neighbouring cell
        elif self.model.movement and self.empty_cells:
            new_pos = self.random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)
