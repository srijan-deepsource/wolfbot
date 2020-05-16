""" troublemaker_test.py """
from conftest import set_roles
from src import const
from src.roles.village import Troublemaker
from src.statements import Statement


class TestTroublemaker:
    """ Tests for the Troublemaker player class. """

    @staticmethod
    def test_awake_init(large_game_roles):
        """
        Should initialize a Troublemaker. Note that the player_index of the Troublemaker is
        not necessarily the index where the true Troublemaker is located.
        """
        player_index = 11
        orig_roles, game_roles = [], list(large_game_roles)
        expected = [
            Statement(
                "I am a Troublemaker and I swapped Player 6 and Player 0.",
                ((11, frozenset({"Troublemaker"})),),
                ((2, 6, 0),),
                "Troublemaker",
            )
        ]
        new_roles = list(large_game_roles)
        new_roles[0], new_roles[6] = new_roles[6], new_roles[0]

        tmkr = Troublemaker.awake_init(player_index, game_roles, orig_roles)

        assert game_roles == new_roles
        assert tmkr.choice_ind1 == 6
        assert tmkr.choice_ind2 == 0
        assert tmkr.statements == expected

    @staticmethod
    def test_get_troublemaker_statements():
        """ Should execute initialization actions and return the possible statements. """
        player_index = 1

        result = Troublemaker.get_troublemaker_statements(player_index, 6, 3)

        assert result == [
            Statement(
                "I am a Troublemaker and I swapped Player 6 and Player 3.",
                ((1, frozenset({"Troublemaker"})),),
                ((2, 6, 3),),
                "Troublemaker",
            )
        ]

    @staticmethod
    def test_get_all_statements():
        """ Should return the possible statements from all possible initialization actions. """
        player_index = 2
        set_roles(("Wolf", "Seer", "Troublemaker", "Villager", "Robber", "Wolf"))
        const.NUM_PLAYERS = 3
        const.NUM_CENTER = 3
        expected_statements = [
            Statement(
                "I am a Troublemaker and I swapped Player 0 and Player 1.",
                ((2, frozenset({"Troublemaker"})),),
                ((2, 0, 1),),
                "Troublemaker",
            )
        ]

        result = Troublemaker.get_all_statements(player_index)

        assert result == expected_statements
