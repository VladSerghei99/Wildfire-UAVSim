# python libraries

import mesa
import functools

# own python modules

from common_fixed_variables import *


class Fire(mesa.Agent):

    def __init__(self, unique_id, model, burning=False):
        super().__init__(unique_id, model)
        self.fuel = random.randint(FUEL_BOTTOM_LIMIT, FUEL_UPPER_LIMIT)
        self.burning = burning
        self.next_burning_state = None
        self.moore = True
        self.radius = 3
        self.selected_dir = 0
        self.steps_counter = 0
        self.cell_prob = 0.0

        # smoke
        self.smoke = Smoke(fire_cell_fuel=self.fuel)

    def is_burning(self):
        return self.burning

    def get_fuel(self):
        return round(self.fuel)

    def get_prob(self):
        return self.cell_prob

    # function that calculates probability of cell s being burned in next time step (p_t+1(s))
    def probability_of_fire(self):
        probs = []
        if self.fuel > 0:
            adjacent_cells = self.model.grid.get_neighborhood(
                self.pos, moore=self.moore, include_center=False, radius=self.radius
            )
            for adjacent in adjacent_cells:
                agents_in_adjacent = self.model.grid.get_cell_list_contents([adjacent])
                for agent in agents_in_adjacent:
                    if type(agent) is Fire:
                        adjacent_burning = 1 if agent.is_burning() else 0
                        # calculates individual probability of burning cell s (self.pos), being influenced by adjacent (s')
                        aux_prob = distance_rate(self.pos, adjacent, self.radius) * adjacent_burning
                        # in this if statement, the wind logic occurs, by biasing the burning cell probability
                        if ACTIVATE_WIND and (adjacent_burning == 1):
                            aux_prob = self.model.wind.apply_wind(aux_prob, self.pos, agent.pos)
                        probs.append(1 - aux_prob)
            if len(probs) == 0:  # if a low tree density is set, this might happen, so it must be checked
                P = 0
            else:
                P = 1 - functools.reduce(lambda a, b: a * b, probs)
        else:
            P = 0
        return P

    def step(self):
        self.steps_counter += 1
        # make fire spread slower
        if self.steps_counter % FIRE_SPREAD_SPEED == 0:
            # if self.steps_counter == 26: # to model how the wind can suddenly change direction
            #     self.model.wind.wind_direction = 'south'
            self.cell_prob = self.probability_of_fire()
            generated = random.random()
            if generated < self.cell_prob:
                self.next_burning_state = True
            else:
                self.next_burning_state = False
            if self.burning and self.fuel > 0:
                self.fuel = self.fuel - BURNING_RATE
            if ACTIVATE_SMOKE:
                self.smoke.smoke_step(self.burning)

    # Mesa framework native method, which is overwritten, necessary for executing changes made in step() method. This
    # logic is required to not update the overall grid state until all cells step() method where executed.
    def advance(self):
        # make fire spread slower
        if self.steps_counter % FIRE_SPREAD_SPEED == 0:
            self.burning = self.next_burning_state


class Smoke:

    def __init__(self, fire_cell_fuel):
        self.smoke = False # activated when fire ignites
        self.dispelling_counter_start_value = fire_cell_fuel
        self.dispelling_lower_bound_start_value = SMOKE_PRE_DISPELLING_COUNTER
        self.dispelling_lower_bound = self.dispelling_lower_bound_start_value
        self.dispelling_counter = self.dispelling_counter_start_value

    def get_dispelling_counter_value(self):
        return self.dispelling_counter

    def get_dispelling_counter_start_value(self):
        return self.dispelling_counter_start_value

    def is_smoke_active(self):
        return self.smoke

    def subtract_dispelling_counter(self):
        self.dispelling_counter -= 1

    # function that updates smoke state and counter based on certain conditions
    def smoke_step(self, burning):
        # if not burning and not self.smoke: pass
        if not self.smoke and self.dispelling_counter == self.dispelling_counter_start_value:
            if ((burning and self.dispelling_lower_bound == self.dispelling_lower_bound_start_value) or
                    (0 < self.dispelling_lower_bound < self.dispelling_lower_bound_start_value)):
                self.dispelling_lower_bound -= 1
            elif self.dispelling_lower_bound == 0:
                self.smoke = True
        elif self.smoke:
            if 0 < self.dispelling_counter <= self.dispelling_counter_start_value:
                self.subtract_dispelling_counter()
            elif self.dispelling_counter == 0:
                self.smoke = False


class Wind:

    def __init__(self):
        self.wind_direction = WIND_DIRECTION

    def change_direction(self):
        if SYSTEM_RANDOM.random() < FIRST_DIR_PROB:
            self.wind_direction = FIRST_DIR
        else:
            self.wind_direction = SECOND_DIR

    def apply_wind(self, aux_prob, relative_center_pos, adjacent_pos):
        if not FIXED_WIND:
            self.change_direction()
            # print("Wind: ", self.wind_direction)
        if self.is_on_wind_direction(relative_center_pos, adjacent_pos):
            aux_prob = aux_prob + (MU * (1 - aux_prob))  # part of 1 I- 'aux_prob' probability is added, depending on mu
        else:
            aux_prob = aux_prob - (MU * aux_prob)   # part of 'aux_prob' probability is removed, depending on mu
        return aux_prob

    def is_on_wind_direction(self, relative_center_pos, adjacent_pos):
        on_wind_direction = False
        if self.wind_direction == 'east':
            if (relative_center_pos[0] > adjacent_pos[0]) and (relative_center_pos[1] == adjacent_pos[1]):
                on_wind_direction = True
        elif self.wind_direction == 'west':
            if (relative_center_pos[0] < adjacent_pos[0]) and (relative_center_pos[1] == adjacent_pos[1]):
                on_wind_direction = True
        elif self.wind_direction == 'north':
            if (relative_center_pos[1] > adjacent_pos[1]) and (relative_center_pos[0] == adjacent_pos[0]):
                on_wind_direction = True
        elif self.wind_direction == 'south':
            if (relative_center_pos[1] < adjacent_pos[1]) and (relative_center_pos[0] == adjacent_pos[0]):
                on_wind_direction = True
        return on_wind_direction


class UAV(mesa.Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.moore = True
        self.selected_dir = 0

    # function that checks if a UAV in a certain position (pos), has another UAV nearby. If so, it can't move, otherwise
    # it will be possible to move.
    def not_UAV_adjacent(self, pos):
        can_move = True
        agents_in_pos = self.model.grid.get_cell_list_contents([pos])
        for agent in agents_in_pos:
            if type(agent) is UAV:
                can_move = False
        return can_move

    def surrounding_states(self):
        surrounding_states = []
        # obtains adjacent cells s' from a concrete cell s (self.pos)
        adjacent_cells = self.model.grid.get_neighborhood(
            self.pos, moore=self.moore, include_center=True, radius=UAV_OBSERVATION_RADIUS
        )
        # obtains each fire cell state, in a list (1 if its burning, 0 if it isn't)
        for cell in adjacent_cells:
            agents = self.model.grid.get_cell_list_contents([cell])
            for agent in agents:
                if type(agent) is Fire:
                    surrounding_states.append(int(agent.is_burning() is True))
        return surrounding_states

    def move(self):
        # directions = [0, 1, 2, 3]  # right, down, left, up
        move_x = [1, 0, -1, 0]
        move_y = [0, -1, 0, 1]
        moved = False

        pos_to_move = (self.pos[0] + move_x[self.selected_dir], self.pos[1] + move_y[self.selected_dir])
        if not self.model.grid.out_of_bounds(pos_to_move) and self.not_UAV_adjacent(pos_to_move):
            self.model.grid.move_agent(self, tuple(pos_to_move))
            moved = True

        return moved

    # Mesa framework native method, which is overwritten, necessary for executing changes made in step() method
    # (as it can be seen, in this case UAVs don't need to update anything in step() method, so it isn't overwritten).
    # This logic is required to not update the overall grid state until all cells step() method where executed.
    def advance(self):
        self.move()
