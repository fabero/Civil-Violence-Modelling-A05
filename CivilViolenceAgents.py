import math
import random
import numpy as np 

from mesa import Agent
from settings import *

FACTOR = 1

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

    susceptibility: (How susceptible is agent to propaganda), U(0,1)

    #propaganda_effect: (For every agent) Will be dynamic

    '''

    @classmethod
    def _get_val_from_uniform_(cls,low=0,high=1):
        return random.uniform(low,high)

    def __init__(
            self,
            unique_id,
            model,
            hardship,
            legitimacy,
            risk_aversion,
            threshold,
            susceptibility,
            propaganda_factor,
            vision,
            pos,
    ):
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
        self.agent_class = POPULATION_AGENT_CLASS
        self.hardship = hardship
        self.legitimacy = legitimacy
        self.grievance = self.hardship * (1 - self.legitimacy)
        self.net_risk = 0 
        self.active = False
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.vision = vision
        self.jail_time = 0
        self.arrest_probability = None
        self.pos = pos

        self.susceptibility = susceptibility
        self.propaganda_factor = propaganda_factor

    def cal_propaganda_effect(self):
        """
            Calculate propaganda effect due to propaganda agents in the vision of current agent.
        """

        #Calculate total propaganda parameter in the neighbourhood by taking the euclidean distance from all propaganda agents
        propaganda_in_vision, bandwagon_in_vision = [], []
        strategy = ""
        count = 0
        for agent in self.neighbors:
            if agent.agent_class == PROPAGANDA_AGENT_CLASS and not agent.jail_time:
                count +=1
                strategy = agent.strategy

                # for TRANSFER
                dist = .0001+np.linalg.norm(np.array([self.pos[0], self.pos[1]], dtype=np.float32) - np.array([agent.pos[0], agent.pos[1]], dtype=np.float32))**2
                propaganda_in_vision.append(1/float(dist))
                
                # for BANDWAGON
                bandwagon_in_vision.append(agent.influence)
        
        # no propaganda effect if no propaganda agents within local vision
        propaganda_effect = 0  

        # assign propaganda effect to the proper formula for the corresponding strategy
        if propaganda_in_vision:
            if strategy == TRANSFER_STRATEGY:
                propaganda_effect = self.susceptibility * sum(propaganda_in_vision)**2 # transfer propaganda effect rule
                self.grievance += min(1, propaganda_effect * self.propaganda_factor)
                

            elif strategy == BANDWAGON_STRATEGY:
                propaganda_effect = self.susceptibility * sum(bandwagon_in_vision)     # bandwagon propaganda effect rule
                self.grievance += self.propaganda_factor * propaganda_effect 


            elif strategy == DEMONIZING_STRATEGY:  
                cop_flag = 1 if self.cops_in_vision else 0     
                propaganda_effect = self.susceptibility * cop_flag                    # demonizing the enemy propaganda effect rule
                self.grievance += propaganda_effect * self.propaganda_factor
        

    def search_neighborhood(self):
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

        self.search_neighborhood()

        """
            Get arrest probability based on number of active agents
            to cop ratio in the neighborhood
        """

        self.cops_in_vision = len(
            [agent for agent in self.neighbors if agent.agent_class == COP_AGENT_CLASS])

        # agent counts herself as active when estimating arrest probability
        self.actives_in_vision = 1 + len(
            [agent for agent in self.neighbors if agent.agent_class == POPULATION_AGENT_CLASS and agent.active and not agent.jail_time])
        
        # defining arrest probability for each agent
        # depending on cop-to-active ratio
        # arrest_prob _constant is defined as 2.3 in the netlogo implementation
        # a rounding to min integer is implemented as suggested in the netlogo
        # implementation
        self.ratio_c_a = int(self.cops_in_vision / self.actives_in_vision)
        self.arrest_probability = (
            1 - math.exp(-1 * self.model.arrest_prob_constant * self.ratio_c_a))

        # calculating net_risk given risk aversion and arrest probability
        # we further calculate a bool value if difference of grievance and net_risk
        # is greater than threshold value which is defined as 0.1 in net logo
        # implementation
        #First update grievance
        self.cal_propaganda_effect()
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
        self.agent_class = COP_AGENT_CLASS
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

        # find the number of visible propaganda agents and active population agents in neighborhood
        actives, propagandas = [], []
        for agent in self.neighbors:
            if agent.agent_class in [POPULATION_AGENT_CLASS] and agent.active and not agent.jail_time:
                actives.append(agent)
            elif agent.agent_class in [PROPAGANDA_AGENT_CLASS] and agent.visible_to_cops and not agent.jail_time:
                propagandas.append(agent)

        # priority of arrest to exposed propaganda agents
        if propagandas:
            self.jail_agent(propagandas)

        # arrest a random active agent and jail her for a random choice of up
        # to JAIL_MAX_TERM steps
        elif actives:
            self.jail_agent(actives)

        # otherwise move if applicable to an empty neighbouring cell
        elif self.model.movement and self.empty_cells:
            new_pos = self.random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)

    # class method for jailing a propaganda/active population agent and moving
    # to their position if applicable
    def jail_agent(self, agents):
        jailed = self.random.choice(agents)
        jailed.jail_time = self.random.randint(1, self.model.max_jail_term)
        # reduce the influence of the propaganda agent for when they become free
        if jailed.agent_class in [PROPAGANDA_AGENT_CLASS]:
            #print('jailed propaganda agent,')
            jailed.total_influence /= jailed.jail_time * FACTOR
            #print('with new total influence after release:{:.4f}'.format(jailed.total_influence)) 
        if self.model.movement:
            self.model.grid.move_agent(self, jailed.pos)

class PropagandaAgent(Agent):
    '''
    Agents who spread propaganada.

    Special Attributes:

    '''

    def __init__(self, unique_id, model, strategy, influence, exposure_threshold, vision, pos):

        super().__init__(unique_id, model)
        self.agent_class = PROPAGANDA_AGENT_CLASS
        self.influence = influence
        self.total_influence = 0
        self.strategy = strategy
        self.exposure_threshold = exposure_threshold
        self.visible_to_cops = False 
        self.jail_time = 0 
        self.vision = vision
        self.pos = pos

    def step(self):

        # no action for jailed agents
        if self.jail_time:
            self.jail_time -= 1
            if not self.jail_time:
                self.visible_to_cops = False
            return

        
        # position of neighborhood cells
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=self.vision)
        # attributes of all the neighboars
        self.neighbors = self.model.grid.get_cell_list_contents(
            self.neighborhood)
        # empty neighborhood cells
        self.empty_cells = [
            cell for cell in self.neighborhood if self.model.grid.is_cell_empty(cell)]

        quiets_in_vision = [agent for agent in self.neighbors if agent.agent_class == POPULATION_AGENT_CLASS and not agent.active and not agent.jail_time]

        # keep track of the total bandwagon influence of propaganda agents for exposure evaluation
        if self.strategy == BANDWAGON_STRATEGY:
            # calculate the **NEW** number of citizens that are influenced 
            for agent in self.neighbors:
                if agent.agent_class in [POPULATION_AGENT_CLASS] and not agent.jail_time and not agent.active:
                    self.total_influence += FACTOR * self.influence * agent.susceptibility / len(quiets_in_vision)
            
            # expose propaganda agent if she has severely influenced the population
            if self.total_influence > self.exposure_threshold:
                self.visible_to_cops = True
            else:
                self.visible_to_cops = False 

        # move if applicable to an empty neighbouring cell
        if self.model.movement and self.empty_cells:
            new_pos = self.random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)




