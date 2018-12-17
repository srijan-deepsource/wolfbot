''' voting.py '''
from statistics import GameResult
from collections import defaultdict
from util import find_all_player_indices
from predictions import make_prediction, print_guesses
from const import logger
import const

def consolidate_results(solver, save_game):
    ''' Consolidates results and returns final GameResult. '''
    ORIGINAL_ROLES, game_roles, all_statements, player_objs = save_game
    if const.USE_VOTING:
        wolf_inds = find_all_player_indices(ORIGINAL_ROLES, 'Wolf')
        all_role_guesses_arr = []
        for i in range(const.NUM_PLAYERS):
            # Good player vs Bad player guesses
            all_solutions = solver(all_statements, i)     # TODO when a wolf becomes good?
            is_evil = i in wolf_inds and player_objs[i].new_role == ''
            is_evil = is_evil or player_objs[i].new_role == 'Wolf'
            all_role_guesses_arr.append(make_prediction(all_solutions, is_evil))

        for prediction in all_role_guesses_arr:
            logger.log(const.logging.TRACE, 'Player prediction: %s', str(prediction))
        all_role_guesses, confidence, guessed_wolf_inds = get_voting_result(all_role_guesses_arr)
        print_guesses(all_role_guesses)
        logger.debug('Confidence level: %s', str([float('{0:0.2f}'.format(n)) for n in confidence]))
        killed_wolf, killed_tanner = eval_wolf_guesses(game_roles, guessed_wolf_inds)
        return GameResult(game_roles, all_role_guesses, all_statements, wolf_inds, killed_wolf, killed_tanner)

    all_solutions = solver(all_statements)
    for solution in all_solutions:
        logger.log(const.logging.TRACE, 'Solver interpretation: %s', str(solution.path))
    all_role_guesses = make_prediction(all_solutions)
    print_guesses(all_role_guesses)
    return GameResult(game_roles, all_role_guesses, all_statements, wolf_inds)


def eval_wolf_guesses(game_roles, guessed_wolf_inds):
    ''' Creates confidence levels for each prediction and selects the most likely Wolf. '''
    if not guessed_wolf_inds:
        logger.info('No wolves were found.')
        final_wolf_inds = find_all_player_indices(game_roles[:const.NUM_PLAYERS], 'Wolf')
        if final_wolf_inds:
            logger.info('Player(s) %s was a Wolf!\n', str(final_wolf_inds))
            return False

        logger.info('That was correct!\n')
        return True

    killed_wolf = False
    killed_tanner = False
    for chosen_wolf in guessed_wolf_inds:
        if game_roles[chosen_wolf] == 'Wolf':
            killed_wolf = True
        elif game_roles[chosen_wolf] == 'Tanner':
            killed_tanner = True
        logger.info('Player %d was chosen as a Wolf.\nPlayer %d was a %s!\n',
                    chosen_wolf, chosen_wolf, game_roles[chosen_wolf])

    if killed_wolf:
        logger.info('Village Team wins!')
    elif killed_tanner:
        logger.info('Tanner wins!')
    else:
        logger.info('Werewolf Team wins!')
    return killed_wolf, killed_tanner


def get_voting_result(all_role_guesses_arr):
    '''
    Take most common role guess array as the final guess for that index.
    guess_histogram stores counts of prediction arrays.
    wolf_votes stores individual votes for Wolves.
    '''
    guess_histogram = defaultdict(int)
    wolf_votes = [0 for _ in range(const.NUM_PLAYERS)]
    for prediction in all_role_guesses_arr:
        guess_histogram[tuple(prediction)] += 1
        for x in range(const.NUM_PLAYERS):
            if prediction[x] == 'Wolf':
                wolf_votes[x] += 1

    guessed_wolf_inds = [i for i, count in enumerate(wolf_votes) if count == max(wolf_votes)]
    all_role_guesses, _ = max(guess_histogram.items(), key=lambda x: x[1])
    confidence = []
    for i in range(const.NUM_ROLES):
        role_dict = defaultdict(int)
        for prediction in all_role_guesses_arr:
            role_dict[prediction[i]] += 1
        count = max(role_dict.values())
        confidence.append(count / const.NUM_PLAYERS)

    return list(all_role_guesses), confidence, guessed_wolf_inds
