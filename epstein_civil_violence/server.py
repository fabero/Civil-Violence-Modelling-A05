from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement, BarChartModule, PieChartModule
from mesa.visualization.UserParam import UserSettableParameter

from .model import EpsteinCivilViolence
from .agent import Citizen, Cop


COP_COLOR = "#000000"
AGENT_QUIET_COLOR = "#0066CC"
AGENT_REBEL_COLOR = "#CC0000"
JAIL_COLOR = "#757575"


def citizen_cop_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "x": agent.pos[0], "y": agent.pos[1],
                 "Filled": "true"}

    if type(agent) is Citizen:
        color = AGENT_QUIET_COLOR if agent.condition == "Quiescent" else \
            AGENT_REBEL_COLOR
        color = JAIL_COLOR if agent.jail_sentence else color
        portrayal["Color"] = color
        portrayal["r"] = 0.8
        portrayal["Layer"] = 0

    elif type(agent) is Cop:
        portrayal["Color"] = COP_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1
    return portrayal

model_params =  {"citizen_density": UserSettableParameter("slider", "Citizen Density", 70, 0, 100,
                                                        description="Initial percentage of citizen in population"),
                        "cop_density": UserSettableParameter("slider", "Cop Density", 4, 0, 100,
                                                        description="Initial percentage of cops in population"),
                        "cop_vision": UserSettableParameter("slider", "Cop Vision", 7, 0, 10,
                                                        description="Number of patches visible to cops"),
                        "citizen_vision": UserSettableParameter("slider", "Citizen Vision", 7, 0, 10,
                                                        description="Number of patches visible to citizens"),
                        "legitimacy": UserSettableParameter("slider", "Government Legitimacy", 80, 0, 100,
                                                        description="Global parameter: Government legitimacy"),
                        "max_jail_term": UserSettableParameter("slider", "Max Jail Term", 30, 0, 1000,
                                                        description="Maximum number of steps that jailed citizens stay in" ),
                        "movement" : UserSettableParameter("checkbox", "Movement", True)
                    }

line_chart = ChartModule([{"Label": "Quiescent", "Color": AGENT_QUIET_COLOR},
                          {"Label": "Active", "Color": AGENT_REBEL_COLOR},
                          {"Label": "Jailed", "Color": JAIL_COLOR}],50,125)


canvas_element = CanvasGrid(citizen_cop_portrayal, 40, 40, 640, 640)
server = ModularServer(EpsteinCivilViolence, [canvas_element, line_chart],
                       "Epstein Civil Violence", model_params)
