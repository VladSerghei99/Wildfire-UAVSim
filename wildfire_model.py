# python libraries

import sys
import mesa
import matplotlib.pyplot as plt

# own python modules

import agents

from common_fixed_variables import *


class WildFireModel(mesa.Model):

    def __init__(self):

        plt.ion()

        self.new_direction_counter = None
        self.datacollector = None
        self.grid = None
        self.unique_agents_id = None
        self.new_direction = None
        self.evaluation_timesteps_counter = None
        self.NUM_AGENTS = NUM_AGENTS
        print(self.NUM_AGENTS)

        self.MR1_LIST = [0.0 for i in range(0, self.NUM_AGENTS)]
        self.MR2_VALUE = 0

        self.reset()

    def reset(self):
        self.unique_agents_id = 0
        # Inverted width and height order, because of matrix accessing purposes, like in many examples:
        #   https://snyk.io/advisor/python/Mesa/functions/mesa.space.MultiGrid
        self.grid = mesa.space.MultiGrid(HEIGHT, WIDTH, False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.set_fire_agents()
        self.wind = agents.Wind()

        x_center = int(HEIGHT / 2)
        y_center = int(WIDTH / 2)

        self.new_direction_counter = 0
        self.evaluation_timesteps_counter = 0

        for a in range(0, self.NUM_AGENTS):
            aux_UAV = agents.UAV(self.unique_agents_id, self)
            y_center += a if a % 2 == 0 else -a
            self.grid.place_agent(aux_UAV, (x_center, y_center + 1))
            self.schedule.add(aux_UAV)
            self.unique_agents_id += 1

        self.datacollector = mesa.DataCollector()
        self.new_direction = [0 for a in range(0, self.NUM_AGENTS)]

    # function that create all fire agents in a grid
    def set_fire_agents(self):
        x_c = int(HEIGHT / 2)
        y_c = int(WIDTH / 2)
        x = [x_c]  # , x_c + 1, x_c - 1
        y = [y_c]  # , y_c + 1, y_c - 1
        for i in range(HEIGHT):
            for j in range(WIDTH):
                # decides to put a "tree" (fire agent) or not
                if SYSTEM_RANDOM.random() < DENSITY_PROB or (i in x and j in y):  # if prob or in center
                    if i in x and j in y:
                        self.new_fire_agent(i, j, True)
                    else:
                        self.new_fire_agent(i, j, False)

    # function that create new fire agent in a concrete cell
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

    def MR1(self, state):
        # total amount of burning cells from state variable
        MR1_reward = [sum(aux_state) for aux_state in state]
        # normalized reward amount for each UAV state
        reward = [normalize(float(reward), N_OBSERVATIONS, 1, 0) for reward in MR1_reward]
        # MR1_list with added rewards
        self.MR1_LIST = [a + b for a, b in zip(self.MR1_LIST, reward)]

    def MR2(self):
        counter = 0
        UAV_agents = [agent for agent in self.schedule.agents if type(agent) is agents.UAV]

        for idx, agent in enumerate(UAV_agents):
            aux_agents_positions = UAV_agents.copy()
            del aux_agents_positions[idx]

            for a in aux_agents_positions:
                x1 = agent.pos[0]
                y1 = agent.pos[1]
                x2 = a.pos[0]
                y2 = a.pos[1]
                distance = euclidean_distance(x1, y1, x2, y2)
                if distance < SECURITY_DISTANCE:
                    counter += 1
        self.MR2_VALUE += counter // 2  # remove duplicate interactions

    def state(self):
        states = []
        for agent in self.schedule.agents:
            if type(agent) is agents.UAV:
                surrounding_states = agent.surrounding_states()
                states.append(surrounding_states)

        for st, _ in enumerate(states):
            counter = len(states[st])
            for i in range(counter, N_OBSERVATIONS):
                states[st].append(0)
        return states

    def step(self):
        self.datacollector.collect(self)

        if BATCH_SIZE == self.evaluation_timesteps_counter - 1:
            print(" --- MR1 --- ")
            print(self.MR1_LIST)
            print(" --- MR2 --- ")
            print(self.MR2_VALUE)
            sys.exit(0)

        if sum(isinstance(i, agents.UAV) for i in self.schedule.agents) > 0:
            # check if simulation ended, if so print MR1 and MR2 overall metrics, and finish loop. Otherwise,
            # keep executing.

            state = self.state()  # s_t
            # self.new_direction is used to execute previous obtained a_t
            self.new_direction = [SYSTEM_RANDOM.choice(range(0, N_ACTIONS))
                                  for i in range(0, self.NUM_AGENTS)]  # a_t

            # TODO: algorithm/s calculation with partial state
            # reward = self.algorithm(state) # r_t+1

            # TODO: an EXAMPLE can be seen. However, your own implementations can be applied as well.
            self.MR1(state)
            self.MR2()

            self.set_drone_dirs()

        self.evaluation_timesteps_counter += 1
        self.schedule.step()
