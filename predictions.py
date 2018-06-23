import const
from const import logger
from copy import deepcopy
import random
import pickle

def make_evil_prediction(solution_arr):
    '''
    Makes the Wolf character's prediction for the game.
    '''
    solution = random.choice(solution_arr)
    all_role_guesses, curr_role_counts = get_basic_guesses(solution)
    # print(all_role_guesses, curr_role_counts)
    solved = recurse_assign(solution, list(all_role_guesses), dict(curr_role_counts), False)

    switch_dict = get_switch_dict(solution)
    final_guesses = [solved[switch_dict[i]] for i in range(len(solved))]
    return final_guesses

def make_predictions_fast(solution):
    '''
    Uses a list of true/false statements and possible role sets
    to return a rushed list of predictions for all roles.
    Does not restrict guesses to the possible sets.
    '''
    all_role_guesses, curr_role_counts = get_basic_guesses(solution)
    solved = recurse_assign(solution, list(all_role_guesses), dict(curr_role_counts), False)
    switch_dict = get_switch_dict(solution)
    final_guesses = [solved[switch_dict[i]] for i in range(len(solved))]
    return final_guesses

def make_predictions(solution_arr):
    '''
    Uses a list of true/false statements and possible role sets
    to return a list of predictions for all roles
    '''
    solved = None
    random.shuffle(solution_arr)
    for solution in solution_arr:
        assert(len(solution.possible_roles) == const.NUM_ROLES)
        all_role_guesses, curr_role_counts = get_basic_guesses(solution)
        solved = recurse_assign(solution, list(all_role_guesses), dict(curr_role_counts))
        if solved: break

    if not solved:
        random.shuffle(solution_arr)
        count = 1
        for solution in solution_arr:
            logger.warning("Could not find solution: " + str(count))
            count += 1
            all_role_guesses, curr_role_counts = get_basic_guesses(solution)
            for j in range(const.NUM_ROLES):
                for role in ['Wolf', 'Robber', 'Insomniac']:
                    if all_role_guesses[j] == role:
                        all_role_guesses[j] = ''
                        curr_role_counts[role] += 1
            solved = recurse_assign(solution, list(all_role_guesses), dict(curr_role_counts))
            if solved: break

    # TODO remove when unnecessary
    if not solved:          # Last resort: assign randomly from curr_role_counts dict
        logger.warning("Choosing without using possible roles (should not happen)")
        solution = random.choice(solution_arr)
        all_role_guesses, curr_role_counts = get_basic_guesses(solution)
        solved = recurse_assign(solution, list(all_role_guesses), dict(curr_role_counts), False)

    switch_dict = get_switch_dict(solution)
    final_guesses = [solved[switch_dict[i]] for i in range(len(solved))]
    return final_guesses

def get_basic_guesses(solution):
    '''
    Populates the basic set of predictions, or adds the empty string if the
    possible roles set is not of size 1. For each statement, take the
    intersection and update the role counts for each character.
    '''
    all_role_guesses = []
    consistent_statements = list(solution.path)
    consistent_roles = deepcopy(solution.possible_roles)
    curr_role_counts = dict(const.ROLE_COUNTS)
    for j in range(const.NUM_ROLES):
        guess_set = consistent_roles[j]
        if j >= len(consistent_statements) or consistent_statements[j]:     # Center card or Player is telling the truth
            for r in const.ROLE_SET:                                        # Remove already chosen cards
                if curr_role_counts[r] == 0:
                    guess_set -= set([r])

            if len(guess_set) == 1:                 # Player is telling the truth
                role = next(iter(guess_set))
                curr_role_counts[role] -= 1
                all_role_guesses.append(role)
            else:
                all_role_guesses.append('')

        elif not consistent_statements[j]:          # Player is lying
            if curr_role_counts['Wolf'] > 0:
                all_role_guesses.append('Wolf')
                curr_role_counts['Wolf'] -= 1
            else:
                all_role_guesses.append('')
    return all_role_guesses, curr_role_counts

def recurse_assign(solution, all_role_guesses, curr_role_counts, restrict_possible=True):
    '''
    Assign the remaining unknown cards by recursing and finding a consistent placement.
    If restrict_possible is enabled, then uses the possible-roles sets to assign.
    '''
    found = True
    for i in range(const.NUM_ROLES):
        if all_role_guesses[i] == '': found = False
    if found: return all_role_guesses

    for i in range(const.NUM_ROLES):
        if all_role_guesses[i] == '':
            if restrict_possible: leftover_roles = list(solution.possible_roles[i])
            else: leftover_roles = [k for k,v in curr_role_counts.items() if v > 0]
            random.shuffle(leftover_roles)
            for r in leftover_roles:
                if curr_role_counts[r] > 0:
                    curr_role_counts[r] -= 1
                    all_role_guesses[i] = r
                    result = recurse_assign(solution, all_role_guesses, curr_role_counts, restrict_possible)
                    if result: return result
                    curr_role_counts[r] += 1
                    all_role_guesses[i] = ''
    return False

def get_switch_dict(solution):
    ''' Converts array of switches into a dictionary to index with. '''
    switch_dict = {i:i for i in range(const.NUM_ROLES)}
    switches = sorted(solution.switches, key=lambda x: x[0])
    for priority, i, j in switches:
        temp = switch_dict[i]
        switch_dict[i] = switch_dict[j]
        switch_dict[j] = temp
    return switch_dict

def print_guesses(all_role_guesses):
    logger.info("\n[Wolfbot] Role guesses: " + str(all_role_guesses[:const.NUM_PLAYERS]) +
                "\n\t  Center cards: " + str(all_role_guesses[const.NUM_PLAYERS:]) + '\n')
