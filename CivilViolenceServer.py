from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule
from utils.hex_gradients import linear_gradient

from CivilViolenceAgents import PopulationAgent, CopAgent, PropagandaAgent
from CivilViolenceModel import CivilViolenceModel

COP_COLOR = "#000000"
AGENT_QUIET_COLOR = "#0066CC"
AGENT_REBEL_COLOR = "#CC0000"
JAIL_COLOR = "#757575"

PROPAGANDA_AGENT_COLOR_JAIL = "#000000"

# start and end hex values for propaganda of an agent
start_prop = "#FFEBE3"
end_prop = "#FF4500"

# we generate an array of hex values in between start and end hex values
# in order to represent agents with an array of propaganda values
# in the grid
grad_propaganda = linear_gradient(start_prop, end_prop, n=100)['hex']

# start and end hex values for susceptibility value of an agent
start_suscep = "#93C5F5"
end_suscep = "#007FFA"

# we generate an array of hex values in between start and end hex values
# in order to represent agents with an array of susceptibility values
# in the grid
grad_suceptibility = linear_gradient(start_suscep, end_suscep, n=100)['hex']

def citizen_cop_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "x": agent.pos[0], "y": agent.pos[1],
                 "Filled": "true"}


    if isinstance(agent, PropagandaAgent):
        '''
        Color for propaganda agent will always remain either out of jail or in jail, it wont have any activation, he is always active
        '''
        # assigning a color from gradient of colors in grad_propaganda list
        # depending on the intensity propaganda value of the agent

        propaganda_value = int(agent.propaganda_value * 100)

        color = PROPAGANDA_AGENT_COLOR_JAIL if agent.jail_time else grad_propaganda[propaganda_value]
        # color = PROPAGANDA_AGENT_COLOR_JAIL if agent.jail_time else PROPAGANDA_AGENT_COLOR_OUT_JAIL
        portrayal['Shape'] = 'rect'
        portrayal["Color"] = color
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["Layer"] = 0


    elif isinstance(agent, PopulationAgent):

        # assigning a color from gradient of colors in grad_susceptibility list
        # depending on the intensity propaganda value of the agent
        susceptibility_value = int(agent.susceptibility * 100)

        color = grad_suceptibility[susceptibility_value] if not agent.active else \
            AGENT_REBEL_COLOR
        color = JAIL_COLOR if agent.jail_time else color
        portrayal["Color"] = color
        portrayal["r"] = 0.8
        portrayal["Layer"] = 1

    elif isinstance(agent, CopAgent):
        portrayal["Color"] = COP_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 2
    return portrayal


model_params = {
    "citizen_density": UserSettableParameter("slider", "Citizen Density", 60, 0, 100,
        description="Initial percentage of citizen in population"),
    "propaganda_agent_density": UserSettableParameter("slider", "Propaganda Agent Density", 10, 0, 100,
        description="Initial percentage of propaganda agent in population"),
    "cop_density": UserSettableParameter("slider", "Cop Density", 4, 0, 100,
        description="Initial percentage of cops in population"),
    "cop_vision": UserSettableParameter("slider", "Cop Vision", 7, 0, 10,
        description="Number of patches visible to cops"),
    "citizen_vision": UserSettableParameter("slider", "Citizen Vision", 7, 0, 10,
        description="Number of patches visible to citizens"),
    "active_threshold": UserSettableParameter("slider", "Active Threshold", 10, 0, 100,
        description="Threshold that agent's Grievance must exceed Net Risk to go active"),
    "legitimacy": UserSettableParameter("slider", "Government Legitimacy", 82, 0, 100,
        description="Global parameter: Government legitimacy"),
    "max_jail_term": UserSettableParameter("slider", "Max Jail Term", 30, 0, 1000,
        description="Maximum number of steps that jailed citizens stay in"),
    "propaganda_factor": UserSettableParameter("slider", "Propaganda Factor", 1, 0, 1000),
    "movement": UserSettableParameter("checkbox", "Movement", True)
}

line_chart = ChartModule([{"Label": "Quiescent", "Color": AGENT_QUIET_COLOR},
                          {"Label": "Active", "Color": AGENT_REBEL_COLOR},
                          {"Label": "Jailed", "Color": JAIL_COLOR},
                          {"Label": "Active Propaganda Agents", "Color": end_prop}], 100, 270)

pie_chart = PieChartModule([{"Label": "Quiescent", "Color": AGENT_QUIET_COLOR},
                            {"Label": "Active", "Color": AGENT_REBEL_COLOR},
                            {"Label": "Jailed", "Color": JAIL_COLOR},
                            {"Label": "Active Propaganda Agents", "Color": end_prop}], 200, 500)

canvas_element = CanvasGrid(citizen_cop_portrayal, 40, 40, 500, 500)
server = ModularServer(CivilViolenceModel, [canvas_element, pie_chart, line_chart],
                       "Epstein Civil Violence Model 1", model_params)

# launch server
if __name__ == '__main__':
    server.launch()
