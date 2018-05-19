from copy import deepcopy
from statements import Statement
import random
import const
from algorithms import switching_solver
from predictions import makePredictions, verifyPredictions
import pickle
import pprint

class Player():
    def __init__(self, player_index):
        self.player = player_index

    def getNextStatement(self, prev=None, possib=None):
        return random.choice(tuple(self.statements))

    def __repr__(self):
        return "<" + self.role + ">"


class Wolf(Player):
    def __init__(self, player_index, wolf_indices):
        super().__init__(player_index)
        self.role = 'Wolf'
        self.statements = self.get_wolf_statements(player_index, wolf_indices)

    @staticmethod
    def get_wolf_statements(player_index, wolf_indices):        # TODO: Have the wolf choose its role ahead of time

        statements = Villager.get_villager_statements(player_index)
        for k in range(const.NUM_CENTER):
            statements += Drunk.get_drunk_statements(player_index, k + const.NUM_PLAYERS)
        for i in range(const.NUM_PLAYERS):
            if player_index != i:
                mason_indices = [player_index, i]
                statements += Mason.get_mason_statements(player_index, mason_indices)

            for j in range(const.NUM_PLAYERS): # Troublemaker should not refer to other wolves or themselves
                if i != j != player_index and i != player_index and i not in wolf_indices and j not in wolf_indices:
                    statements += Troublemaker.get_troublemaker_statements(player_index, i, j)

            # Wolf-seer more likely to declare they saw a villager
            for role in const.ROLES:
                if i not in wolf_indices:
                    if role != 'Seer':      # "Hey, I'm a Seer and I saw another Seer..."
                        statements += Seer.get_seer_statements(player_index, i, role)
                    if role != 'Wolf':      # "I robbed a Wolf and now I'm a Wolf..."
                        statements += Robber.get_robber_statements(player_index, i, role)
        return statements
    
    def getNextStatement(self, previousStatements, possible_statements):
        def expectimax(statement_list, ind, depth=None):
            #legal_actions = state.getLegalActions(agent)
            #if depth == 0:
            #    return self.evaluationFunction(state), None
            if ind == const.NUM_PLAYERS:
                sol = switching_solver(statement_list)
                all_role_guesses = makePredictions(sol)
                pprint.pprint(statement_list)
                print(all_role_guesses)
                return 0, None # TODO
            if ind == self.player: # It's Me 
                values = [expectimax(deepcopy(statement_list) + [statement], ind + 1, depth-1) for statement in self.statements]
                vals = [v[0] for v in values]
                best_move = self.statements[vals.index(max(vals))]
                return max(vals), best_move
            else:
                values = [expectimax(deepcopy(statement_list) + [statement], ind + 1, depth-1) for statement in possible_statements[ind]]
                vals = [v[0] for v in values]
                return sum(vals)/len(vals), None         
        return random.choice(tuple(self.statements))
        best_val, best_move =  expectimax(previousStatements, self.player, 5)
        return best_move


class Seer(Player):
    def __init__(self, player_index, seer_peek_index, seer_peek_character):
        super().__init__(player_index)
        self.role = 'Seer'
        self.statements = self.get_seer_statements(player_index, seer_peek_index, seer_peek_character)

    @staticmethod
    def get_seer_statements(player_index, seen_index, seen_role):
        sentence = "I am a Seer and I saw that Player " + str(seen_index) + " was a " + str(seen_role) + "."
        knowledge = [(player_index, {'Seer'}), (seen_index, {seen_role})]
        return [Statement(sentence, knowledge)]


class Villager(Player):
    def __init__(self, player_index):
        super().__init__(player_index)
        self.role = 'Villager'
        self.statements = self.get_villager_statements(player_index)

    @staticmethod
    def get_villager_statements(player_index):
        return [Statement("I am a Villager." , [(player_index, {'Villager'})])]


class Mason(Player):
    def __init__(self, player_index, mason_indices):
        super().__init__(player_index)
        self.role = 'Mason'
        self.statements = self.get_mason_statements(player_index, mason_indices)

    @staticmethod
    def get_mason_statements(player_index, mason_indices):
        if len(mason_indices) == 1:
            sentence = "I am a Mason. The other Mason is not present."
            knowledge = [(player_index, {'Mason'})]
            for ind in range(const.NUM_PLAYERS):
                if ind != player_index:
                    knowledge.append((ind, {role for role in const.ROLES} - {'Mason'}))
        else:
            otherMason = mason_indices[0] if mason_indices[0] != player_index else mason_indices[1]
            sentence = "I am a Mason. The other Mason is Player " + str(otherMason) + '.'
            knowledge = [(player_index, {'Mason'}), (otherMason, {'Mason'})]
        return [Statement(sentence, knowledge)]


class Robber(Player):
    def __init__(self, player_index, robber_choice_index, robber_choice_character):
        super().__init__(player_index)
        self.role = 'Robber'
        self.statements = self.get_robber_statements(player_index, robber_choice_index, robber_choice_character)

    @staticmethod
    def get_robber_statements(player_index, robber_choice_index, robber_choice_character):
        # TODO if robber_choice_character != 'Wolf':
        sentence = "I am a Robber and I swapped with Player " + str(robber_choice_index) + \
                    ". I am now a " + robber_choice_character + "."
        knowledge = [(player_index, {'Robber'}), (robber_choice_index, {robber_choice_character})]
        switches = [(const.ROBBER_PRIORITY, robber_choice_index, player_index)]
        return [Statement(sentence, knowledge, switches)]


class Troublemaker(Player):
    def __init__(self, player_index, trblmkr_index1, trblmkr_index2):
        super().__init__(player_index)
        self.role = 'Troublemaker'
        self.statements = self.get_troublemaker_statements(player_index, trblmkr_index1, trblmkr_index2)

    @staticmethod
    def get_troublemaker_statements(player_index, trblmkr_index1, trblmkr_index2):
        sentence = "I am a Troublemaker and I swapped Player " + str(trblmkr_index1) + \
                    " with Player " + str(trblmkr_index2) + "."
        knowledge = [(player_index, {'Troublemaker'})]
        switches = [(const.TRBLMKR_PRIORITY, trblmkr_index1, trblmkr_index2)]
        return [Statement(sentence, knowledge, switches)]

class Drunk(Player):
    def __init__(self, player_index, drunk_choice_index):
        super().__init__(player_index)
        self.role = 'Drunk'
        self.statements = self.get_drunk_statements(player_index, drunk_choice_index)

    @staticmethod
    def get_drunk_statements(player_index, drunk_choice_index):
        sentence = "I am a Drunk and I swapped with Center " + \
                    str(drunk_choice_index - const.NUM_PLAYERS) + "."
        knowledge = [(player_index, {'Drunk'})]
        switches = [(const.DRUNK_PRIORITY, drunk_choice_index, player_index)]
        return [Statement(sentence, knowledge, switches)]

class Insomniac(Player):
    def __init__(self, player_index, new_insomniac_index, insomniac_new_role):
        super().__init__(player_index)
        self.role = 'Insomniac'
        self.statements = self.get_insomniac_statements(player_index, new_insomniac_index, insomniac_new_role)

    @staticmethod
    def get_insomniac_statements(player_index, new_insomniac_index, insomniac_new_role):
        sentence = "I was the Insomniac and when I woke up I was a " + str(insomniac_new_role) + "."
        return [Statement(sentence, [(player_index, {'Insomniac'})])]

#import pprint
#possib = get_possible_statements()
#pprint.pprint(possib)
#with open('possible_statements.pkl', 'wb') as f: pickle.dump(possib, f)
