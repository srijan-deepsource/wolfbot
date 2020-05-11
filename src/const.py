""" const.py """
import argparse
import logging
import random
import sys
from collections import Counter
from enum import IntEnum, unique


@unique
class Priority(IntEnum):
    """ Priorities for Statement order. """

    ROBBER, TROUBLEMAKER, DRUNK = 1, 2, 3


@unique
class StatementLevel(IntEnum):
    """ Statement Priority Levels """

    NOT_YET_SPOKEN = -1
    NO_INFO = 0
    SOME_INFO = 5
    PRIMARY = 10


UNIT_TEST = "pytest" in sys.modules
if UNIT_TEST:
    random.seed(0)


def init_program() -> argparse.Namespace:
    """ Command Line Arguments """
    parser = argparse.ArgumentParser(description="config constants for main.py")
    # fmt: off
    parser.add_argument("--user", "-u", action="store_true", default=False,
                        help="enable interactive mode")
    parser.add_argument("--num_games", "-n", type=int, default=1,
                        help="specify number of games")
    parser.add_argument("--info", "-i", action="store_true", default=False,
                        help="enable logging.INFO")
    parser.add_argument("--replay", "-r", action="store_true", default=False,
                        help="replay previous game")
    # fmt: on
    return parser.parse_args("" if UNIT_TEST else sys.argv[1:])


ARGS = init_program()

""" Game Constants """
ROLES = (
    "Drunk",
    "Insomniac",
    "Hunter",
    "Mason",
    "Mason",
    "Minion",
    "Robber",
    "Seer",
    "Tanner",
    "Troublemaker",
    "Wolf",
    "Wolf",
    "Villager",
    "Villager",
    "Villager",
)
NUM_CENTER = 3
# Disabling this is good for testing solvers.
USE_VOTING = True
# Randomize or use literally the order of the ROLES constant above.
RANDOMIZE_ROLES = True
# Enable multi-statement rounds.
MULTI_STATEMENT = True

""" Simulation Constants """
NUM_GAMES = ARGS.num_games
MAX_LOG_GAMES = 10
FIXED_WOLF_INDEX = -1
SAVE_REPLAY = NUM_GAMES < MAX_LOG_GAMES
REPLAY_FILE = "data/replay.json"
REPLAY_STATE = "data/replay_state.json"
REPLAY = ARGS.replay

""" Util Constants """
ROLE_SET = frozenset(ROLES)
SORTED_ROLE_SET = sorted(ROLE_SET)
NUM_ROLES = len(ROLES)
ROLE_COUNTS = dict(Counter(ROLES))  # Dict of {'Villager': 3, 'Wolf': 2, ... }
NUM_PLAYERS = NUM_ROLES - NUM_CENTER

""" Game Rules """
AWAKE_ORDER = ("Wolf", "Minion", "Mason", "Seer", "Robber", "Troublemaker", "Drunk", "Insomniac")
VILLAGE_ROLES = {
    "Villager",
    "Mason",
    "Seer",
    "Robber",
    "Troublemaker",
    "Drunk",
    "Insomniac",
    "Hunter",
} & ROLE_SET
EVIL_ROLES = {"Tanner", "Wolf", "Minion"} & ROLE_SET

""" Basic Wolf Player (Pruned statement set) """
USE_REG_WOLF = True
CENTER_SEER_PROB = 0.9

""" Expectimax Wolf Player """
USE_EXPECTIMAX_WOLF = False
EXPECTIMAX_DEPTH = 1
BRANCH_FACTOR = 5

""" Reinforcement Learning Wolf Player """
USE_RL_WOLF = False
EXPERIENCE_PATH = "src/learning/simulations/wolf_player.json"

""" Interactive Game Constants """
INTERACTIVE_MODE_ON = ARGS.user
IS_USER = [False] * NUM_ROLES
NUM_OPTIONS = 5

""" Logging Constants
TRACE = Debugging mode for development
DEBUG = Include all hidden messages
INFO = Regular gameplay
WARNING = Results only """
TRACE = 5
logging.basicConfig(format="%(message)s", level=TRACE)  # filename='test1.txt', filemode='a')
logger = logging.getLogger()

if NUM_GAMES >= 10 and not UNIT_TEST:
    logger.setLevel(logging.WARNING)
elif ARGS.info or INTERACTIVE_MODE_ON:
    logger.setLevel(logging.INFO)

""" Ensure only one Wolf version is active """
assert not (USE_EXPECTIMAX_WOLF and USE_RL_WOLF)

if sys.version_info < (3, 0):
    sys.stdout.write("Requires Python 3, not Python 2!\n")
    sys.exit()
