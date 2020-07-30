""" gameresults.py """
# pylint: disable=missing-function-docstring
from typing import Tuple

import pytest

from src.stats import GameResult


@pytest.fixture
def example_small_game_result(small_game_roles: Tuple[str, ...]) -> GameResult:
    return GameResult(("Villager", "Seer", "Robber"), ("Villager", "Seer", "Robber"), (), "Village")


@pytest.fixture
def example_medium_game_result(medium_game_roles: Tuple[str, ...]) -> GameResult:
    return GameResult(
        ("Seer", "Wolf", "Troublemaker", "Drunk", "Minion", "Robber"),
        ("Seer", "Minion", "Troublemaker", "Drunk", "Wolf", "Robber"),
        (1,),
        "Werewolf",
    )


@pytest.fixture
def example_large_game_result(large_game_roles: Tuple[str, ...]) -> GameResult:
    return GameResult(
        (
            "Villager",
            "Insomniac",
            "Mason",
            "Tanner",
            "Villager",
            "Drunk",
            "Seer",
            "Wolf",
            "Minion",
            "Villager",
            "Wolf",
            "Hunter",
            "Troublemaker",
            "Mason",
            "Robber",
        ),
        (
            "Villager",
            "Mason",
            "Mason",
            "Minion",
            "Villager",
            "Drunk",
            "Wolf",
            "Wolf",
            "Seer",
            "Villager",
            "Tanner",
            "Hunter",
            "Insomniac",
            "Troublemaker",
            "Robber",
        ),
        (7, 10),
        "Village",
    )
