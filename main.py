# python libraries

import mesa

from Canvas_Grid_Visualization import CanvasGrid

# own python modules

import wildfire_model
import agents

from common_fixed_variables import *


# creates agent dictionary for rendering it on Canvas Gird
def agent_portrayal(agent):
    portrayal = {"Shape": "rect", "Filled": True, "h": 1, "w": 1}
    if PROBABILITY_MAP:
        if type(agent) is agents.Fire:
            idx = int(round(agent.get_prob(), 1) * 10)
            portrayal.update({"Color": BLACK_AND_WHITE_COLORS[idx], "Layer": 0})
    elif BURNING_FLAGS_MAP:
        if type(agent) is agents.Fire:
            if agent.is_burning():
                color = "Black"
            else:
                color = "White"
            portrayal.update({"Color": color, "Layer": 0})
    else:
        if type(agent) is agents.Fire:
            if agent.smoke.is_smoke_active():
                idx = normalize_fuel_values(agent.smoke.get_dispelling_counter_value(),
                                            agent.smoke.get_dispelling_counter_start_value())
                portrayal.update({"Color": SMOKE_COLORS[idx], "Layer": 0})
            else:
                if agent.is_burning():
                    idx = normalize_fuel_values(agent.get_fuel(), FUEL_UPPER_LIMIT)
                    portrayal.update({"Color": FIRE_COLORS[idx], "Layer": 0})  # "#ff5d00" -> fire orange
                else:
                    idx = normalize_fuel_values(agent.get_fuel(), FUEL_UPPER_LIMIT)
                    portrayal.update({"Color": VEGETATION_COLORS[idx], "Layer": 0})
        elif type(agent) is agents.UAV:
            portrayal.update({"Color": "Black", "Layer": 1, "h": 0.8, "w": 0.8})
    return portrayal


def main():
    print('actions:', N_ACTIONS)
    print('observations:', N_OBSERVATIONS)

    grid = CanvasGrid(agent_portrayal, WIDTH, HEIGHT, 10 * WIDTH, 10 * HEIGHT)
    # initialize Modular server for mesa Python visualization
    server = mesa.visualization.ModularServer(wildfire_model.WildFireModel, [grid], "WildFire Model")
    server.port = 8521  # The default
    server.launch()


main()
