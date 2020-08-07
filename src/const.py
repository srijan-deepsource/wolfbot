""" const.py """
from __future__ import annotations

import argparse
import functools
import logging
import math
import random
import sys
from collections import Counter
from enum import Enum, IntEnum, auto, unique
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, TypeVar

from src.log import OneNightLogger

# TODO https://github.com/PyCQA/pylint/issues/3401
T = TypeVar("T")  # pylint: disable=invalid-name
CACHED_FUNCTIONS = []


def lru_cache(  # pylint: disable=protected-access
    func: Callable[..., T]
) -> functools._lru_cache_wrapper[T]:
    """ Allows lru_cache to type check correctly. """
    new_func = functools.lru_cache()(func)
    CACHED_FUNCTIONS.append(new_func)
    return new_func


def init_program(is_unit_test: bool) -> argparse.Namespace:
    """ Command Line Arguments """
    parser = argparse.ArgumentParser(description="config constants for main.py")
    # fmt: off
    parser.add_argument("--num_games", "-n", type=int, default=1,
                        help="specify number of games")
    parser.add_argument("--log_level", "-l", type=str, choices=["trace", "debug", "info", "warn"],
                        help="set logging level")
    parser.add_argument("--replay", "-r", action="store_true", default=False,
                        help="replay previous game")
    parser.add_argument("--seed", "-s",
                        help="specify game seed")
    parser.add_argument("--user", "-u", action="store_true", default=False,
                        help="enable interactive mode")
    # fmt: on
    return parser.parse_args("" if is_unit_test else sys.argv[1:])


def get_counts(arr: Sequence[T]) -> Dict[T, int]:
    """
    Returns a dict of counts of each item in a list. When there are fewer than ~40 items, using
    a regular dictionary is faster than using a Counter.
    """
    if len(arr) < 40:
        counts: Dict[T, int] = {}
        for item in arr:
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1
        return counts

    return dict(Counter(arr))


@unique
@functools.total_ordering
class Role(Enum):
    """ Role Type. """

    DRUNK = "Drunk"
    HUNTER = "Hunter"
    INSOMNIAC = "Insomniac"
    MASON = "Mason"
    MINION = "Minion"
    NONE = ""
    ROBBER = "Robber"
    SEER = "Seer"
    TANNER = "Tanner"
    TROUBLEMAKER = "Troublemaker"
    WOLF = "Wolf"
    VILLAGER = "Villager"

    @lru_cache
    def __lt__(self, other: object) -> bool:
        """ This function is necessary to make Role sortable alphabetically. """
        if not isinstance(other, Role):
            raise NotImplementedError
        result = self.value < other.value  # pylint: disable=comparison-with-callable
        assert isinstance(result, bool)
        return result

    @lru_cache
    def __repr__(self) -> str:  # pylint: disable=invalid-repr-returned
        assert isinstance(self.value, str)
        return self.value

    @lru_cache
    def __format__(self, formatstr: str) -> str:  # pylint: disable=invalid-format-returned
        del formatstr
        assert isinstance(self.value, str)
        return self.value

    def json_repr(self) -> Dict[str, Any]:
        """ Gets JSON representation of a Role enum. """
        return {"type": "Role", "data": self.value}


ARGS = init_program("pytest" in sys.modules)
if ARGS.seed:
    random.seed(ARGS.seed)

# Game Constants
# These are the player roles used in a game.
ROLES = (
    Role.DRUNK,
    Role.INSOMNIAC,
    Role.HUNTER,
    Role.MASON,
    Role.MASON,
    Role.MINION,
    Role.ROBBER,
    Role.SEER,
    Role.TANNER,
    Role.TROUBLEMAKER,
    Role.WOLF,
    Role.WOLF,
    Role.VILLAGER,
    Role.VILLAGER,
    Role.VILLAGER,
)
NUM_CENTER = 3
# Randomize or use literally the order of the ROLES constant above.
RANDOMIZE_ROLES = True
# Enable multi-statement rounds.
MULTI_STATEMENT = False

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
NUM_UNIQUE_ROLES = len(SORTED_ROLE_SET)
ROLE_COUNTS = get_counts(ROLES)  # Dict of {Role.VILLAGER: 3, Role.WOLF: 2, ... }
NUM_PLAYERS = NUM_ROLES - NUM_CENTER
ROLE_TO_BITS = {role: i for i, role in enumerate(SORTED_ROLE_SET)}
BITS_TO_ROLE = {i: role for i, role in enumerate(SORTED_ROLE_SET)}


class RoleBits(int):
    """ Acts like a Set. """

    def __new__(cls, *args: Role, val: Optional[int] = None) -> int:  # , *args, **kwargs):
        if args:
            new_bits = super().__new__(cls, 0)
            for role in args:
                assert role in SORTED_ROLE_SET  # TODO REMOVE
                new_bits = new_bits.set_bit(ROLE_TO_BITS[role], True)
            return new_bits

        val = (1 << NUM_UNIQUE_ROLES) - 1 if val is None else val
        return super().__new__(cls, val)

    @staticmethod
    def binary_str(val: int) -> str:
        coerced_positive_val = val & (2 ** NUM_UNIQUE_ROLES - 1)
        return f"{coerced_positive_val:0{NUM_UNIQUE_ROLES}b}"

    def __repr__(self) -> str:
        return self.binary_str(self)

    def set_bit(self, index: int, new_val: bool) -> RoleBits:
        """ Mark an index as the given value of its current state. """
        assert index < NUM_UNIQUE_ROLES
        reversed_index = NUM_UNIQUE_ROLES - index - 1
        if new_val:
            return RoleBits(val=self | 1 << reversed_index)
        else:
            return RoleBits(val=self & ~(1 << reversed_index))

    @property
    def is_solo(self) -> bool:
        int_self = int(self)
        return int_self != 0 and (int_self & (int_self - 1)) == 0

    @property
    def solo_role(self) -> Role:
        """ Assumes is_solo is True. """
        assert self.is_solo
        return BITS_TO_ROLE[NUM_UNIQUE_ROLES - int(math.log2(int(self))) - 1]

    @property
    def as_tuple(self) -> Tuple[Role, ...]:
        result = [BITS_TO_ROLE[i] for i, bit in enumerate(str(self)) if int(bit) == 1]
        return tuple(result)

    def __bool__(self) -> bool:
        return self != 0

    def __len__(self) -> int:  # TODO REMOVE
        return NUM_UNIQUE_ROLES

    def __contains__(self, other: object) -> bool:
        """ Intersection of two role sets. """
        assert isinstance(other, Role)
        if other not in ROLE_TO_BITS:
            return False
        return self & (1 << ROLE_TO_BITS[other]) != 0

    def __eq__(self, other: object) -> bool:
        """ Intersection of two role sets. """
        assert isinstance(other, RoleBits)
        return super().__eq__(other)

    def __neq__(self, other: object) -> bool:
        """ Intersection of two role sets. """
        assert isinstance(other, RoleBits)
        return not super().__eq__(other)

    def __invert__(self) -> RoleBits:
        """ Inverts all bits. """
        return RoleBits(val=~int(self)) & (2 ** NUM_UNIQUE_ROLES - 1)

    def __and__(self, other: object) -> RoleBits:
        """ Intersection of two role sets. """
        if isinstance(other, Role):
            return RoleBits(val=self & (1 << ROLE_TO_BITS[other]))
        if isinstance(other, (RoleBits, int)):
            return RoleBits(val=super().__and__(other))
        raise TypeError

    def __iand__(self, other: object) -> RoleBits:  # TODO REMOVE
        """ Intersection of two role sets. """
        return self.__and__(other)

    def __or__(self, other: object) -> RoleBits:
        """ Intersection of two role sets. """
        if isinstance(other, Role):
            return RoleBits(val=self | (1 << ROLE_TO_BITS[other]))
        if isinstance(other, (RoleBits, int)):
            return RoleBits(val=super().__or__(other))
        raise TypeError

    def __ior__(self, other: object) -> RoleBits:
        """ Intersection of two role sets. """
        return self.__or__(other)

    def __sub__(self, other: object) -> RoleBits:
        """ Intersection of two role sets. """
        if isinstance(other, Role):
            new_bits = self.set_bit(ROLE_TO_BITS[other], False)
            return new_bits
        raise TypeError

    def __isub__(self, other: object) -> RoleBits:
        """ Intersection of two role sets. """
        return self.__sub__(other)

    def __hash__(self) -> int:
        return hash(self)

    def json_repr(self) -> Dict[str, Any]:
        return {"type": "RoleBits", "data": self}


ROLE_BITSET = RoleBits(*ROLE_SET)


""" Game Rules """
AWAKE_ORDER = (
    Role.WOLF,
    Role.MINION,
    Role.MASON,
    Role.SEER,
    Role.ROBBER,
    Role.TROUBLEMAKER,
    Role.DRUNK,
    Role.INSOMNIAC,
)

VILLAGE_ROLES = (
    frozenset(
        {
            Role.VILLAGER,
            Role.MASON,
            Role.SEER,
            Role.ROBBER,
            Role.TROUBLEMAKER,
            Role.DRUNK,
            Role.INSOMNIAC,
            Role.HUNTER,
        }
    )
    & ROLE_SET
)
EVIL_ROLES = frozenset({Role.TANNER, Role.WOLF, Role.MINION}) & ROLE_SET

VILLAGE_ROLE_BITS = RoleBits(val=0)
for role in VILLAGE_ROLES:
    VILLAGE_ROLE_BITS = VILLAGE_ROLE_BITS & role

EVIL_ROLES_BITS = RoleBits(val=0)
for role in EVIL_ROLES:
    EVIL_ROLES_BITS &= role

""" Village Players """
CENTER_SEER_PROB = 0.9
SMART_VILLAGERS = True

""" Werewolf Players """
# Basic Wolf Player (Pruned statement set)
USE_REG_WOLF = True

# Expectimax Wolf, Minion, Tanner
EXPECTIMAX_WOLF = False
EXPECTIMAX_DEPTH = 1
BRANCH_FACTOR = 5
EXPECTIMAX_TANNER = False
EXPECTIMAX_MINION = EXPECTIMAX_WOLF

# Reinforcement Learning Wolf
USE_RL_WOLF = False
EXPERIENCE_PATH = "src/learning/simulations/wolf.json"

""" Interactive Game Constants """
INTERACTIVE_MODE = ARGS.user
IS_USER = [False] * NUM_ROLES
USER_ROLE = Role.NONE
NUM_OPTIONS = 5
INFLUENCE_PROB = 0.1

""" Logging """
logger = OneNightLogger()

if ARGS.log_level:
    log_levels = {
        "trace": logger.trace_level,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
    }
    logger.set_level(log_levels[ARGS.log_level])
elif INTERACTIVE_MODE:
    logger.set_level(logging.INFO)


assert USER_ROLE is Role.NONE or USER_ROLE in ROLES
assert not (EXPECTIMAX_WOLF and USE_RL_WOLF)
if sys.version_info < (3, 8):
    sys.stdout.write("Python " + sys.version)
    sys.stdout.write("\n\nWolfBot requires Python 3.8+ to work!\n\n")
    sys.exit()


@unique
class SwitchPriority(IntEnum):
    """ Priorities for switch actions, in order that they are performed. """

    ROBBER, TROUBLEMAKER, DRUNK = 1, 2, 3


@unique
class StatementLevel(IntEnum):
    """ Statement Priority Levels. Only the order of the values matters. """

    NOT_YET_SPOKEN = -1
    NO_INFO = 0
    SOME_INFO = 5
    PRIMARY = 10


@unique
class Team(Enum):
    """ Team names, order doesn't matter. """

    VILLAGE, TANNER, WEREWOLF = auto(), auto(), auto()

    def json_repr(self) -> Dict[str, Any]:
        """ Gets JSON representation of a Role enum. """
        return {"type": "Team", "data": self.value}
