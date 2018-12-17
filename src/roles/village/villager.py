''' villager.py '''
from statements import Statement
from .player import Player

class Villager(Player):
    ''' Villager Player class. '''

    def __init__(self, player_index):
        super().__init__(player_index)
        self.role = 'Villager'
        self.statements = self.get_villager_statements(player_index)

    @staticmethod
    def get_villager_statements(player_index):
        ''' Gets Villager Statement. '''
        return [Statement('I am a Villager.', [(player_index, {'Villager'})])]

    @staticmethod
    def get_all_statements(player_index):
        ''' Required for all player types. Returns all possible role statements. '''
        return Villager.get_villager_statements(player_index)
