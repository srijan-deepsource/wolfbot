''' possible.py '''
import const
from ...village import Villager, Mason, Seer, Robber, Troublemaker, Drunk, Insomniac

def get_expected_statements(wolf_indices):
    '''
    Gets all possible statements that can be made by another player from any index.
    Used to find the 'expect' part of the Expectimax algorithm.
    '''
    possible = {}
    for player_index in range(const.NUM_PLAYERS):
        possible[player_index] = []
        if 'Villager' in const.ROLE_SET:
            possible[player_index] += Villager.get_villager_statements(player_index)
        if 'Insomniac' in const.ROLE_SET:
            for role in const.ROLES:
                if role != 'Wolf':
                    possible[player_index] += Insomniac.get_insomniac_statements(player_index, role)
        if 'Mason' in const.ROLE_SET:
            possible[player_index] += Mason.get_mason_statements(player_index, [player_index])
            for i in range(const.NUM_PLAYERS):
                if player_index != i:
                    mason_indices = [player_index, i]
                    possible[player_index] += Mason.get_mason_statements(player_index, mason_indices)
        if 'Drunk' in const.ROLE_SET:
            for k in range(const.NUM_CENTER):
                possible[player_index] += Drunk.get_drunk_statements(player_index, k + const.NUM_PLAYERS)
        if 'Troublemaker' in const.ROLE_SET:
            for i in range(const.NUM_PLAYERS):
                for j in range(i+1, const.NUM_PLAYERS):
                    if i != j != player_index and i != player_index: # Troublemaker should not switch themselves
                        possible[player_index] += Troublemaker.get_troublemaker_statements(player_index, i, j)
        if 'Robber' in const.ROLE_SET:
            for i in range(const.NUM_PLAYERS):
                for role in const.ROLES:
                    if role != 'Wolf' and role != 'Robber':      # 'I robbed Player 0 and now I'm a Wolf...'
                        possible[player_index] += Robber.get_robber_statements(player_index, i, role)
        if 'Seer' in const.ROLE_SET:
            for role in const.ROLES:
                for i in range(const.NUM_PLAYERS):
                    if role not in ['Seer', 'Wolf'] and i not in wolf_indices:      # 'Hey, I'm a Seer and I saw another Seer...'
                        possible[player_index] += Seer.get_seer_statements(player_index, i, role)
            for i in wolf_indices:
                possible[player_index] += Seer.get_seer_statements(player_index, i, 'Wolf')
            for c1 in range(const.NUM_CENTER):
                for c2 in range(c1 + 1, const.NUM_CENTER):
                    for role1 in const.ROLES:
                        for role2 in const.ROLES:
                            if role1 != 'Seer' and role2 != 'Seer' and c1 != c2:
                                if role1 != role2 or const.ROLE_COUNTS[role1] >= 2:
                                    possible[player_index] += Seer.get_seer_statements(player_index, c1  + const.NUM_PLAYERS, role1,
                                                                                       c2 + const.NUM_PLAYERS, role2)
    return possible