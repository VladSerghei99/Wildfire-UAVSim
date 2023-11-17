# python libraries

import os
import mesa
import numpy
import statistics
import matplotlib.pyplot as plt
import matplotlib as mpl

# own python modules

import agents

from common_fixed_variables import *


class WildFireModel(mesa.Model):

    def __init__(self):

        plt.ion()

        # wildfiremodel exclusive vars

        self.new_direction_counter = None
        self.datacollector = None
        self.grid = None
        self.unique_agents_id = None

        # in widlfiremodel, but used by DQN

        self.new_direction = None
        self.NUM_AGENTS = NUM_AGENTS # Number of UAV (IMPORTANT, for auto-eval max number required)
        print(self.NUM_AGENTS)

        self.reset()

    def reset(self):
        self.unique_agents_id = 0
        # Inverted width and height order, because of matrix accessing purposes, like in many examples:
        #   https://snyk.io/advisor/python/Mesa/functions/mesa.space.MultiGrid
        self.grid = mesa.space.MultiGrid(HEIGHT, WIDTH, False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.set_fire_agents()
        self.wind = agents.Wind()
        # set two UAV
        x_center = int(HEIGHT / 2)
        y_center = int(WIDTH / 2)

        self.new_direction_counter = 0

        for a in range(0, self.NUM_AGENTS):
            aux_UAV = agents.UAV(self.unique_agents_id, self)
            y_center += a if a % 2 == 0 else -a
            self.grid.place_agent(aux_UAV, (x_center, y_center + 1))
            self.schedule.add(aux_UAV)
            self.unique_agents_id += 1

        self.datacollector = mesa.DataCollector()
        self.new_direction = [0 for a in range(0, self.NUM_AGENTS)]

    def set_fire_agents(self):
        x_c = int(HEIGHT / 2)
        y_c = int(WIDTH / 2)
        x = [x_c]  # , x_c + 1, x_c - 1
        y = [y_c]  # , y_c + 1, y_c - 1
        for i in range(HEIGHT):
            for j in range(WIDTH):
                # decides to put a "tree" (fire agent) or not
                if SYSTEM_RANDOM.random() < DENSITY_PROB or (i in x and j in y): # if prob or in center
                    if i in x and j in y:
                        self.new_fire_agent(i, j, True)
                    else:
                        self.new_fire_agent(i, j, False)

    def new_fire_agent(self, pos_x, pos_y, burning):
        source_fire = agents.Fire(self.unique_agents_id, self, burning)
        self.unique_agents_id += 1
        self.schedule.add(source_fire)
        self.grid.place_agent(source_fire, tuple([pos_x, pos_y]))

    def set_drone_dirs(self):
        self.new_direction_counter = 0
        for agent in self.schedule.agents:
            if type(agent) is agents.UAV:
                agent.selected_dir = self.new_direction[self.new_direction_counter]
                self.new_direction_counter += 1

    def state(self):
        states = []
        UAV_positions = []
        for agent in self.schedule.agents:
            if type(agent) is agents.UAV:
                surrounding_states = agent.surrounding_states()
                states.append(surrounding_states)
                UAV_positions.append(agent.pos)

        # when UAV reaches edge or corner, takes less surrounding states, so fulfilling the vector till
        # maximum amount of observation is necessary. It is IMPORTANT to mention that this COULD AFFECT to
        # the correct behaviour of drones when these are trying to maintain distance with other, because of
        # less area is taking into account. Either way, in most cases this is expendable.
        for st, _ in enumerate(states):
            counter = len(states[st])
            for i in range(counter, N_OBSERVATIONS):
                states[st].append(0)
        return states

    def step(self):
        self.datacollector.collect(self)
        if sum(isinstance(i, agents.UAV) for i in self.schedule.agents) > 0:
            state = self.state()  # s_t
            self.new_direction = [SYSTEM_RANDOM.choice(range(0, N_ACTIONS))
                                  for i in range(0, self.NUM_AGENTS)]  # a_t

            # algorithm/s calculation with partial state

            # analytics

            self.set_drone_dirs()
        self.schedule.step()  # self.new_direction is used to execute previous obtained a_t
