import random

# COMMON VARIABLES

SYSTEM_RANDOM = random.SystemRandom()  # ... Not available on all systems ... (Python official doc)

# activation simulator params (environment conditions)

FIXED_WIND = True
ACTIVATE_SMOKE = True
ACTIVATE_WIND = True
# To avoid throwing "KeyError: 'Layer'" when prob or flag burning maps are shown,
# so UAV won't get its "Layer" attribute in the "portrayal_method(obj)", NUM_AGENTS must
# be set to 0.
PROBABILITY_MAP = False
BURNING_FLAGS_MAP = False

# model logic params

NUM_AGENTS = 0
FUEL_BOTTOM_LIMIT = 7
UAV_OBSERVATION_RADIUS = 8
side = ((UAV_OBSERVATION_RADIUS * 2) + 1)  # allows to build a square side
N_OBSERVATIONS = side * side  # calculates the observation square
BATCH_SIZE = 90
N_ACTIONS = 4
WIDTH = 60  # in python [height, width] for grid, in js [width, heigh]
HEIGHT = 60

# forest params

DENSITY_PROB = 1  # Tree density (Float number in the interval [0, 1])
BURNING_RATE = 1
WIND_DIRECTION = 'north'
if not FIXED_WIND:
    # Possible mixed wind directions: NW, NE, SW, SE"
    FIRST_DIR = 'north'  # Introduce first wind direction (north, south, east, west):
    SECOND_DIR = 'west'  # Introduce second wind direction (probability calculated based on first one),
    FIRST_DIR_PROB = 0.95  # "Introduce first wind probability [0, 1]
MU = 0.85  # Wind velocity (Float number in the interval [0, 1])
FIRE_SPREAD_SPEED = 2
FUEL_UPPER_LIMIT = 10

VEGETATION_COLORS = ["#414141", "#9eff89", "#85e370", "#72d05c", "#62c14c", "#459f30", "#389023", "#2f831b",
                     "#236f11", "#1c630b", "#175808", "#124b05"]  # index is remaining fuel when IT ISN'T burning
FIRE_COLORS = ["#414141", "#d8d675", "#eae740", "#fefa01", "#fed401", "#feaa01", "#fe7001", "#fe5501",
               "#fe3e01", "#fe2f01", "#fe2301", "#fe0101"]  # index is remaining fuel when IT IS burning
SMOKE_COLORS = ["#c8c8c8", "#c2c2c2", "#bbbbbb", "#b4b4b4", "#b1b1b1", "#ababab", "#a2a2a2", "#9b9b9b",
                "#949494", "#8f8f8f", "#8a8a8a", "#808080"]  # index is smoke density
BLACK_AND_WHITE_COLORS = ["#ffffff", "#e6e6e6", "#c9c9c9", "#b1b1b1", "#a1a1a1", "#818181", "#636363",
                          "#474747", "#303030", "#1a1a1a", "#000000"]
COLORS_LEN = len(VEGETATION_COLORS)


# functions

# function that normalize fuel values to fit them with vegetation and fire colors
def normalize_fuel_values(fuel, limit):
    if fuel > limit:
        fuel = limit
    return max(0, round((fuel / limit) * COLORS_LEN - 1))
