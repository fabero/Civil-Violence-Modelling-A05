from mesa import Agent


class PopulationAgent(Agent):
    """An agent that can become active."""
    def __init__(self, unique_id, model, hardship, legitimacy, risk_aversion, threshold, vision, position):
        super().__init__(unique_id, model)
        self.hardship = hardship
        self.legitimacy = legitimacy
        self.grievance = self.hardship * (1 - self.legitimacy)
        self.active = False
        self.risk_aversion = risk_aversion
        self.agent_class = 'population'
        self.threshold = threshold
        self.vision = vision
        self.jail_term = 0
        self.arrest_probability = None
        self.position = position

    def step(self):
        
        """
            If an agent is jailed it cannot move in the grid
            For each step, their jailterm will be reduced by 1
        """

        if self.jail_term:
            self.jail_term -= 1
            return


        """
            Get information of the neighborhood.
            Get all the neighbors info and empty cells in neighborhood
        """

        # position of neighborhood cells
        self.neighborhood = self.model.grid.get_neighborhood(self.position,
                                                             moore=False,
                                                             radius=1)
        # attributes of all the neighboars
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
        # empty neighborhood cells
        self.empty_cells = [cell for cell in self.neighborhood if self.model.grid.is_cell_empty(cell)]


        """
            Get arrest probability based on number of active agents
            to cop ratio in the neighborhood
        """

        cops_in_vision = len([agent for agent in self.neighbors if agent.agent_class == "cop"])

        # not entirely sure if agent counts themself as active too
        # in order to calculate arrest probability in the paper(cross-check)
        actives_in_vision = 1

        for agent in self.neighbors:
            if(agent.agent_class == "population" and
                agent.active == True and
                agent.jail_term == 0):

                actives_in_vision += 1

        # defining arrest probability for each agent
        # depending on cop is to active population agent ratio
        # arrest_prob _constant is defined as 2.3 in the netlogo implementation
        self.ratio_c_a =  cops_in_vision/actives_in_vision
        self.arrest_probability = (1 - math.exp(-1 * self.model.arrest_prob_constant)*self.ratio_c_a)

        # calculating net_risk given risk aversion and arrest probability
        # we further calculate a bool value if difference of grievance and net_risk
        # is greater than threshold value which is defined as 0.1 in net logo implementation
        self.net_risk = self.risk_aversion * self.arrest_probability
        thresh_bool = (self.grievance - self.net_risk) > threshold


        # simple state transition for population agent
        # Case 1: if state is inactive and thresh bool is true
        # then transition to an active state, set active flag to true
        # Case 2: if active flag is true but thresh bool has changes to false
        # then transition back to inactive state
        if self.active ==  False and thresh_bool:
            self.active = True
        elif self.active == True and not thresh_bool:
            self.active = False

        # movement rule: randomly move to empty neighborhood cells
        # around your current position
        if self.model.movement and self.empty_cells:
            new_position = self.random.choice(self.empty_cells)
            self.model.gride.move_agent(self, new_position)
        
                
        
