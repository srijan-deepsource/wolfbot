""" conftest.py """
import csv
import os
import random
from collections.abc import Callable
from typing import Any

import pytest

from fixtures import (  # pylint: disable=unused-import
    example_large_game_result,
    example_large_saved_game,
    example_large_solverstate,
    example_medium_game_result,
    example_medium_saved_game,
    example_medium_solved_list,
    example_medium_solverstate,
    example_medium_solverstate_list,
    example_medium_solverstate_solved,
    example_small_game_result,
    example_small_saved_game,
    example_small_solverstate,
    example_small_solverstate_solved,
    example_statement,
    large_individual_preds,
    large_knowledge_base,
    large_statement_list,
    medium_knowledge_base,
    medium_statement_list,
    small_knowledge_base,
    small_statement_list,
)
from src import const
from src.const import Role
from src.util import verify_const


def set_roles(*roles: Role) -> None:
    """ Changes to ROLES should propagate to all of its descendants. """
    const.ROLES = roles  # type: ignore[assignment]
    const.ROLE_SET = frozenset(const.ROLES)
    const.SORTED_ROLE_SET = sorted(const.ROLE_SET)
    const.ROLE_COUNTS = const.get_counts(const.ROLES)
    const.NUM_ROLES = len(const.ROLES)
    const.VILLAGE_ROLES &= const.ROLE_SET
    const.EVIL_ROLES &= const.ROLE_SET
    const.IS_USER = [False] * const.NUM_ROLES


@pytest.fixture(autouse=True)
def _reset_const(seed: int = 0) -> None:
    """
    This fixture sets the constants for ALL unit + integration tests.

    IMPORTANT:
    -   No caching is able to be used between different tests, as some
        cached functions have side effects because they rely on other constants.
    -   All random() methods are monkeypatched to always return the same result.
        This was done to prevent results from changing when new calls to random()
        are added. Beware of using random() functions in any loop or sequence.
    """
    random.seed(seed)
    const.logger.set_level(0)
    const.NUM_PLAYERS = 12
    const.NUM_CENTER = 3
    const.VILLAGE_ROLES = frozenset(
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
    const.EVIL_ROLES = frozenset({Role.TANNER, Role.WOLF, Role.MINION})

    # Game Modes
    const.RANDOMIZE_ROLES = True
    const.MULTI_STATEMENT = False
    const.INTERACTIVE_MODE = False

    # Village Settings
    const.CENTER_SEER_PROB = 0.9
    const.SMART_VILLAGERS = True
    const.USE_RELAXED_SOLVER = False

    # Werewolf Settings
    const.USE_REG_WOLF = False
    const.EXPECTIMAX_WOLF = False
    const.EXPECTIMAX_MINION = False
    const.EXPECTIMAX_TANNER = False
    const.RL_WOLF = False

    const.REPLAY_FILE = "unit_test/test_data/replay.json"
    set_roles(
        Role.INSOMNIAC,
        Role.VILLAGER,
        Role.ROBBER,
        Role.VILLAGER,
        Role.DRUNK,
        Role.WOLF,
        Role.WOLF,
        Role.SEER,
        Role.TANNER,
        Role.MASON,
        Role.MINION,
        Role.TROUBLEMAKER,
        Role.VILLAGER,
        Role.MASON,
        Role.HUNTER,
    )
    verify_const()

    for cached_function in const.CACHED_FUNCTIONS:
        cached_function.cache_clear()


@pytest.fixture
def small_game_roles() -> tuple[Role, ...]:
    const.NUM_PLAYERS = 3
    const.NUM_CENTER = 0
    set_roles(Role.VILLAGER, Role.SEER, Role.ROBBER)
    return const.ROLES


@pytest.fixture
def medium_game_roles() -> tuple[Role, ...]:
    const.NUM_PLAYERS = 5
    const.NUM_CENTER = 1
    set_roles(
        Role.ROBBER, Role.DRUNK, Role.WOLF, Role.TROUBLEMAKER, Role.SEER, Role.MINION
    )
    return const.ROLES


@pytest.fixture
def large_game_roles() -> tuple[Role, ...]:
    const.NUM_PLAYERS = 12
    const.NUM_CENTER = 3
    set_roles(
        Role.WOLF,
        Role.VILLAGER,
        Role.ROBBER,
        Role.SEER,
        Role.VILLAGER,
        Role.TANNER,
        Role.MASON,
        Role.WOLF,
        Role.MINION,
        Role.MASON,
        Role.DRUNK,
        Role.VILLAGER,
        Role.TROUBLEMAKER,
        Role.INSOMNIAC,
        Role.HUNTER,
    )
    return const.ROLES


@pytest.fixture
def standard_game_roles() -> tuple[Role, ...]:
    const.NUM_PLAYERS = 7
    const.NUM_CENTER = 3
    set_roles(
        Role.VILLAGER,
        Role.VILLAGER,
        Role.VILLAGER,
        Role.SEER,
        Role.WOLF,
        Role.WOLF,
        Role.TROUBLEMAKER,
        Role.MASON,
        Role.MASON,
        Role.DRUNK,
    )
    return const.ROLES


@pytest.fixture
def override_random(monkeypatch: pytest.MonkeyPatch, seed: int = 0) -> None:
    """ Overrides all functions from the built-in random module. """

    def fix_seed(orig_function: Callable[..., Any]) -> Callable[..., Any]:
        """
        Returns the exact same function, but adds a call to random.seed(0) first.
        Ensures idempotency, which means that, for example, multiple
        random.shuffle() calls always produce the same result.
        """

        def fixed_seed_version(param: Any, *args: Any, **kwargs: Any) -> Any:
            """ Sets the random seed and then returns the original function result. """
            random.seed(seed)
            return orig_function(param, *args, **kwargs)

        return fixed_seed_version

    def fixed_seed_shuffle(param: Any) -> Any:
        """ Sets the random seed and then returns the original function result. """
        random.seed(seed)
        param = random.sample(param, len(param))

    monkeypatch.setattr("random.choice", fix_seed(random.choice))
    monkeypatch.setattr("random.choices", fix_seed(random.choices))
    monkeypatch.setattr("random.randrange", fix_seed(random.randrange))
    monkeypatch.setattr("random.shuffle", fixed_seed_shuffle)


def override_input(inputs: list[str]) -> Callable[[str], str]:
    """
    Returns a new input() function that accepts a string and repeatedly pops strings
    from the front the provided list and returns them as calls to input().
    """

    def _input(prompt: str) -> str:
        """
        The new input() function. Prints a prompt and then modifies the provided list.
        """
        print(prompt)
        if not inputs:
            raise RuntimeError("Not enough inputs provided.")
        return inputs.pop(0)

    return _input


def write_results(stat_results: dict[str, float], file_path: str) -> None:
    """ Writes stat_results to corresponding csv file. """
    sub_folder, filename = os.path.split(file_path)
    destination = os.path.join("integration_test", "results", sub_folder)
    if not os.path.isdir(destination):
        os.makedirs(destination)

    results_filename = os.path.join(destination, filename)
    with open(results_filename, "a+") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=stat_results)
        if os.path.getsize(results_filename) == 0:
            writer.writeheader()
        writer.writerow(stat_results)


def verify_output_file(caplog: pytest.LogCaptureFixture, filename: str) -> None:
    """ Helper method for comparing file output differences. """
    with open(filename) as output_file:
        expected = tuple(output_file.read().split("\n"))
    verify_output(caplog, expected)


def verify_output(caplog: pytest.LogCaptureFixture, expected: tuple[str, ...]) -> None:
    """ Helper method for comparing logging output differences. """
    captured = list(map(lambda x: x.getMessage(), caplog.records))
    assert "\n".join(captured) == "\n".join(expected)


def verify_output_string(caplog: pytest.LogCaptureFixture, expected: str) -> None:
    """ Helper method for comparing string output differences. """
    assert caplog.records[0].getMessage() == expected
