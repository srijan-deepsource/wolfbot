''' const.py '''
from collections import Counter
import random
# random.seed(0)
import logging

''' Game Constants '''
ROLES = ('Insomniac', 'Villager', 'Villager', 'Villager', 'Wolf', 'Wolf', 'Seer', 'Tanner',
         'Mason', 'Mason', 'Drunk', 'Troublemaker', 'Robber', 'Minion', 'Hunter')
NUM_CENTER = 3
USE_VOTING = True
RANDOMIZE_ROLES = True

''' Util Constants '''
ROLE_SET = set(ROLES)
NUM_ROLES = len(ROLES)
ROLE_COUNTS = dict(Counter(ROLES))  # Dict of {'Villager': 3, 'Wolf': 2, ... }
NUM_PLAYERS = NUM_ROLES - NUM_CENTER
ROBBER_PRIORITY, TROUBLEMAKER_PRIORITY, DRUNK_PRIORITY = 1, 2, 3

''' Basic Wolf Player (Pruned statement set) '''
USE_REG_WOLF = True

''' Expectimax Wolf Player '''
USE_EXPECTIMAX_WOLF = True
EXPECTIMAX_DEPTH = 1
BRANCH_FACTOR = 5

''' Reinforcement Learning Wolf Player '''
USE_RL_WOLF = False
EXPERIENCE_PATH = 'src/learning/simulations/wolf_player.json'

''' Simulation Constants '''
NUM_GAMES = 1
SHOW_PROGRESS = False or NUM_GAMES >= 10
FIXED_WOLF_INDEX = None
SAVE_REPLAY = NUM_GAMES < 10

''' Interactive Game Constants '''
INTERACTIVE_MODE_ON = False
IS_USER = [False for _ in range(NUM_ROLES)]
if INTERACTIVE_MODE_ON:
    IS_USER[random.randint(0, NUM_PLAYERS - 1)] = True

''' Logging Constants '''
logging.basicConfig(format='%(message)s', level=logging.INFO)
logging.TRACE = 5
logger = logging.getLogger()
logger.setLevel(logging.TRACE)
if NUM_GAMES >= 10: logger.setLevel(logging.WARNING)
if INTERACTIVE_MODE_ON: logger.setLevel(logging.INFO)
'''
TRACE = Debugging mode for development
DEBUG = Include all hidden messages
INFO = Regular gameplay
WARNING = Results only
'''

''' Ensure only one Wolf version is active '''
assert sum([USE_EXPECTIMAX_WOLF, USE_RL_WOLF]) <= 1
