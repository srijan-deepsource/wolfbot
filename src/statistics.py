''' statistics.py '''
from collections import Counter
from const import logger
import const

class GameResult:
    ''' Each round of one_night returns a GameResult. '''
    def __init__(self, actual, guessed, statements, wolf_inds, winning_team=''):
        self.actual = actual
        self.guessed = guessed
        self.statements = statements
        self.wolf_inds = wolf_inds
        self.winning_team = winning_team

    def json_repr(self):
        ''' Returns json representation of the GameResult. '''
        return {
            'type': 'GameResult',
            'actual': self.actual,
            'guessed': self.guessed,
            'statements': self.statements,
            'wolf_inds': self.wolf_inds,
            'winning_team': self.winning_team
        }


class Statistics:
    ''' Initialize a Statistics object. '''
    def __init__(self):
        self.metrics = [self.correctness_strict, self.correctness_lenient_center,
                        self.wolf_predictions_one, self.wolf_predictions_all,
                        self.wolf_predictions_center]
        if const.USE_VOTING:
            self.metrics.append(self.villager_wins)
            self.metrics.append(self.tanner_wins)
            self.metrics.append(self.werewolf_wins)
        self.correct = [0.0 for _ in range(len(self.metrics))]
        self.total = [0.0 for _ in range(len(self.metrics))]
        self.match1, self.match2 = 0.0, 0.0
        self.num_games = 0

    def add_result(self, game_result):
        ''' Updates the Statistics object with a GameResult. '''
        self.num_games += 1
        for metric_index in range(len(self.metrics)):
            func = self.metrics[metric_index]
            corr, tot = func(game_result)
            self.correct[metric_index] += corr
            self.total[metric_index] += tot

    def print_statistics(self):
        ''' Outputs overall statistics of inputed game results. '''
        logger.warning('\nNumber of Games: %d', self.num_games)
        sentences = [
            'Accuracy for all predictions: ',
            'Accuracy with lenient center scores: ',
            'S1: Found at least 1 Wolf player: ',
            'S2: Found all Wolf players: ',
            'Percentage of correct Wolf guesses (including center Wolves): ',
            'Percentage of Villager Team wins: ',
            'Percentage of Tanner Team wins: ',
            'Percentage of Werewolf Team wins: '
        ]
        assert len(sentences) == len(self.metrics)
        for i in range(len(self.metrics)):
            if self.total[i] == 0: self.total[i] += 1
            logger.warning('%s%s', sentences[i], str(self.correct[i] / self.total[i]))

    @staticmethod
    def correctness_strict(game_result):
        ''' Returns fraction of how many roles were guessed correctly out of all roles. '''
        correct = 0.0
        for i in range(const.NUM_ROLES):
            if game_result.actual[i] == game_result.guessed[i]:
                correct += 1
        return correct, const.NUM_ROLES

    @staticmethod
    def correctness_lenient_center(game_result):
        '''
        Returns fraction of how many player roles were guessed correctly.
        Optionally adds a bonus for a matching center set.
        '''
        correct = const.NUM_CENTER
        for i in range(const.NUM_PLAYERS):
            if game_result.actual[i] == game_result.guessed[i]:
                correct += 1
        center_set = dict(Counter(game_result.actual[const.NUM_PLAYERS:]))
        center_set2 = game_result.guessed[const.NUM_PLAYERS:]
        for guess in center_set2:
            if guess not in center_set or center_set[guess] == 0:
                correct -= 1
            else:
                center_set[guess] -= 1
        return correct, const.NUM_ROLES

    @staticmethod
    def wolf_predictions_one(game_result):
        ''' Returns 1/1 if at least one Wolf was correctly identified. '''
        correct_guesses = 0
        total_wolves = 1
        for i in range(const.NUM_PLAYERS):
            if game_result.actual[i] == 'Wolf' == game_result.guessed[i]:
                correct_guesses += 1
        return int(correct_guesses > 0), total_wolves

    @staticmethod
    def wolf_predictions_all(game_result):
        ''' Returns 1/1 if all Wolves were correctly identified. '''
        correct_guesses = 0
        total_wolves = 0
        for i in range(const.NUM_PLAYERS):
            if game_result.actual[i] == 'Wolf':
                total_wolves += 1
                if game_result.guessed[i] == 'Wolf':
                    correct_guesses += 1
        return int(correct_guesses == total_wolves), 1

    @staticmethod
    def wolf_predictions_center(game_result):
        ''' Returns fraction of how many Wolves were correctly identified. '''
        correct_guesses = 0
        total_wolves = 0
        for i in range(const.NUM_ROLES):
            if game_result.actual[i] == 'Wolf':
                total_wolves += 1
                if game_result.guessed[i] == 'Wolf':
                    correct_guesses += 1
        return correct_guesses, total_wolves

    @staticmethod
    def villager_wins(game_result):
        ''' Returns 1/1 if the Villager team won. '''
        return int(game_result.winning_team == 'Villager'), 1

    @staticmethod
    def tanner_wins(game_result):
        ''' Returns 1/1 if the Tanner won. '''
        return int(game_result.winning_team == 'Tanner'), 1

    @staticmethod
    def werewolf_wins(game_result):
        ''' Returns 1/1 if the Werewolf team won. '''
        return int(game_result.winning_team == 'Werewolf'), 1
