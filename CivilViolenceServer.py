from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement, BarChartModule, PieChartModule
from mesa.visualization.UserParam import UserSettableParameter

from CivilViolenceModel import CivilViolenceModel
from CivilViolenceAgents import PopulationAgent, CopAgent,PropagandaAgent

COP_COLOR = "#000000"
AGENT_QUIET_COLOR = "#0066CC"
AGENT_REBEL_COLOR = "#CC0000"
JAIL_COLOR = "#757575"

PROPAGANDA_AGENT_COLOR_JAIL = "#00FF00"

PROPAGANDA_AGENT_COLOR_OUT_JAIL = "#FF4500"




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
        # color = AGENT_QUIET_COLOR if not agent.active else \
        #     AGENT_REBEL_COLOR
        color = PROPAGANDA_AGENT_COLOR_JAIL if agent.jail_time else PROPAGANDA_AGENT_COLOR_OUT_JAIL
        portrayal['Shape'] = 'rect'
        portrayal["Color"] = color
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["Layer"] = 0


    elif isinstance(agent, PopulationAgent):
        color = AGENT_QUIET_COLOR if not agent.active else \
            AGENT_REBEL_COLOR
        color = JAIL_COLOR if agent.jail_time else color
        portrayal["Color"] = color
        portrayal["r"] = 0.8
        portrayal["Layer"] = 0

    elif isinstance(agent, CopAgent):
        portrayal["Color"] = COP_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1
    return portrayal


model_params = {
    "citizen_density": UserSettableParameter(
        "slider",
        "Citizen Density",
        70,
        0,
        100,
        description="Initial percentage of citizen in population"),
    "propaganda_agent_density": UserSettableParameter(
        "slider",
        "Propaganda Agent Density",
        20,
        0,
        100,
        description="Initial percentage of propaganda agent in population"),
    "cop_density": UserSettableParameter(
        "slider",
        "Cop Density",
        4,
        0,
        100,
        description="Initial percentage of cops in population"),
    "cop_vision": UserSettableParameter(
        "slider",
        "Cop Vision",
        7,
        0,
        10,
        description="Number of patches visible to cops"),
    "citizen_vision": UserSettableParameter(
        "slider",
        "Citizen Vision",
        7,
        0,
        10,
        description="Number of patches visible to citizens"),
    "legitimacy": UserSettableParameter(
        "slider",
        "Government Legitimacy",
        82,
        0,
        100,
        description="Global parameter: Government legitimacy"),
    "max_jail_term": UserSettableParameter(
        "slider",
        "Max Jail Term",
        30,
        0,
        1000,
        description="Maximum number of steps that jailed citizens stay in"),
    "movement": UserSettableParameter(
        "checkbox",
        "Movement",
        True),
    "propaganda_allowed": UserSettableParameter(
        "checkbox",
        "Allow Propaganda",
        True)
}

line_chart = ChartModule([{"Label": "Quiescent", "Color": AGENT_QUIET_COLOR},
                          {"Label": "Active", "Color": AGENT_REBEL_COLOR},
                          {"Label": "Jailed", "Color": JAIL_COLOR}], 50, 125)


canvas_element = CanvasGrid(citizen_cop_portrayal, 40, 40, 640, 640)
server = ModularServer(CivilViolenceModel, [canvas_element, line_chart],
                       "Epstein Civil Violence Model 1", model_params)

# launch server
if __name__ == '__main__':
    server.launch()
