""" villager_test.py """
from src.roles.village import Villager
from src.statements import Statement


class TestVillager:
    """ Tests for the Villager player class. """

    @staticmethod
    def test_awake_init():
        """ Should initialize a Villager. """
        player_index = 5

        villager = Villager.awake_init(player_index, (), ())  # Other params are unused.

        assert villager.statements == [Statement("I am a Villager.", ((5, {"Villager"}),))]

    @staticmethod
    def test_get_villager_statements():
        """ Should execute initialization actions and return the possible statements. """
        player_index = 0

        result = Villager.get_villager_statements(player_index)

        assert result == [Statement("I am a Villager.", ((0, {"Villager"}),))]

    @staticmethod
    def test_get_all_statements():
        """ Should return the possible statements from all possible initialization actions. """
        player_index = 2

        result = Villager.get_all_statements(player_index)

        assert result == [Statement("I am a Villager.", ((2, {"Villager"}),))]
