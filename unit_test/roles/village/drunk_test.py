""" drunk_test.py """
from typing import Tuple

from conftest import set_roles
from src import const
from src.const import Role, RoleBits, SwitchPriority
from src.roles import Drunk
from src.statements import Statement


class TestDrunk:
    """ Tests for the Drunk player class. """

    @staticmethod
    def test_awake_init(large_game_roles: Tuple[Role, ...]) -> None:
        """
        Should initialize a Drunk. Note that the player_index of the Drunk is not necessarily
        the index where the true Drunk is located.
        """
        player_index = 6
        game_roles = list(large_game_roles)
        new_roles = list(large_game_roles)
        new_roles[13], new_roles[6] = new_roles[6], new_roles[13]

        drunk = Drunk.awake_init(player_index, game_roles, large_game_roles)

        assert drunk.choice_ind == 13
        assert game_roles == new_roles
        assert drunk.statements == (
            Statement(
                "I am a Drunk and I swapped with Center 1.",
                ((6, RoleBits(Role.DRUNK)),),
                ((SwitchPriority.DRUNK, 6, 13),),
                Role.DRUNK,
            ),
        )

    @staticmethod
    def test_get_drunk_statements() -> None:
        """ Should execute initialization actions and return the possible statements. """
        player_index = 4

        result = Drunk.get_drunk_statements(player_index, 12)

        assert result == (
            Statement(
                "I am a Drunk and I swapped with Center 0.",
                ((4, RoleBits(Role.DRUNK)),),
                ((SwitchPriority.DRUNK, 4, 12),),
                Role.DRUNK,
            ),
        )

    @staticmethod
    def test_get_all_statements() -> None:
        """ Should return the possible statements from all possible initialization actions. """
        player_index = 2
        set_roles(Role.WOLF, Role.SEER, Role.DRUNK, Role.VILLAGER, Role.ROBBER, Role.WOLF)
        const.NUM_PLAYERS = 3
        const.NUM_CENTER = 3
        expected_statements = (
            Statement(
                "I am a Drunk and I swapped with Center 0.",
                ((2, RoleBits(Role.DRUNK)),),
                ((SwitchPriority.DRUNK, 2, 3),),
                Role.DRUNK,
            ),
            Statement(
                "I am a Drunk and I swapped with Center 1.",
                ((2, RoleBits(Role.DRUNK)),),
                ((SwitchPriority.DRUNK, 2, 4),),
                Role.DRUNK,
            ),
            Statement(
                "I am a Drunk and I swapped with Center 2.",
                ((2, RoleBits(Role.DRUNK)),),
                ((SwitchPriority.DRUNK, 2, 5),),
                Role.DRUNK,
            ),
        )

        result = Drunk.get_all_statements(player_index)

        assert result == expected_statements
