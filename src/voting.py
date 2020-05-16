""" voting.py """
import random
from typing import Dict, List, Tuple

from src import const, util
from src.algorithms import switching_solver as solver
from src.const import logger
from src.predictions import make_prediction, make_random_prediction
from src.roles import Player
from src.statements import Statement
from src.stats import GameResult, SavedGame


def consolidate_results(save_game: SavedGame) -> GameResult:
    """ Consolidates results and returns final GameResult. """
    original_roles, game_roles, all_statements, player_objs = save_game.load_game()
    orig_wolf_inds = util.find_all_player_indices(original_roles, "Wolf")

    if const.USE_VOTING:
        indiv_preds = get_individual_preds(player_objs, all_statements, orig_wolf_inds)
        all_guesses, confidence, guessed_wolf_inds, vote_inds = get_voting_result(indiv_preds)
        util.print_roles(game_roles, "Solution", const.INFO)
        util.print_roles(all_guesses, "WolfBot")
        logger.debug(f"Confidence levels: {[float(f'{conf:.2f}') for conf in confidence]}")
        winning_team = eval_final_guesses(game_roles, guessed_wolf_inds, vote_inds)
        return GameResult(game_roles, all_guesses, orig_wolf_inds, winning_team)

    all_solutions = solver(tuple(all_statements))
    for solution in all_solutions:
        logger.log(const.TRACE, f"Solver interpretation: {solution.path}")
    all_role_guesses = make_prediction(all_solutions)
    util.print_roles(all_role_guesses, "WolfBot")
    return GameResult(game_roles, all_role_guesses, orig_wolf_inds)


def is_player_evil(player_objs: List[Player], i: int, orig_wolf_inds: List[int]) -> bool:
    """ Decide whether a character is about to make an evil prediction. """
    # TODO When a wolf becomes good? Do I need to check for Wolf twice?
    return (
        (i in orig_wolf_inds and player_objs[i].new_role == "")
        or (player_objs[i].role in const.EVIL_ROLES and player_objs[i].new_role == "")
        or player_objs[i].new_role in const.EVIL_ROLES
    )


def get_individual_preds(
    player_objs: List[Player], all_statements: List[Statement], orig_wolf_inds: List[int]
) -> List[List[str]]:
    """ Let each player make a prediction of every player's true role. """
    all_role_guesses_arr = []
    # Good player vs Bad player guesses
    for i in range(const.NUM_PLAYERS):
        is_evil = is_player_evil(player_objs, i, orig_wolf_inds)
        if const.SMART_VILLAGERS or is_evil:
            all_solutions = solver(tuple(all_statements), (i,))
            prediction = make_prediction(all_solutions, is_evil)
        else:
            prediction = make_random_prediction()
        all_role_guesses_arr.append(prediction)

    logger.log(const.TRACE, "\n[Trace] Predictions:")
    number_length = len(str(const.NUM_ROLES))
    for i, pred in enumerate(all_role_guesses_arr):
        logger.log(const.TRACE, f"Player {i:{number_length}}: {pred}".replace("'", ""))

    return all_role_guesses_arr


def eval_final_guesses(
    game_roles: List[str], guessed_wolf_inds: List[int], vote_inds: List[int]
) -> str:
    """ Decide which team won based on the final vote. """
    killed_wolf, killed_tanner, villager_win = False, False, False
    if len(guessed_wolf_inds) == const.NUM_PLAYERS:
        logger.info("No wolves were found.")
        final_wolf_inds = util.find_all_player_indices(game_roles, "Wolf")
        if final_wolf_inds:
            logger.info(f"But Player(s) {final_wolf_inds} was a Wolf!\n")
        else:
            logger.info("That was correct!\n")
            villager_win = True
    else:
        # Hunter kills the player he voted for if he dies.
        # Ensure player did not vote themselves in this case.
        for i in guessed_wolf_inds:
            logger.info(f"Player {i} was chosen as a Wolf.\nPlayer {i} was a {game_roles[i]}!\n")
            if game_roles[i] == "Hunter" and i != vote_inds[i]:
                if vote_inds[i] not in guessed_wolf_inds:
                    guessed_wolf_inds.append(vote_inds[i])
                logger.info(f"(Player {i}) Hunter died and killed Player {vote_inds[i]} too!\n")
            elif game_roles[i] == "Wolf":
                killed_wolf = True
            elif game_roles[i] == "Tanner":
                killed_tanner = True

    if villager_win or killed_wolf:
        logger.info("Village Team wins!")
        return "Villager"

    if killed_tanner:
        logger.info("Tanner wins!")
        return "Tanner"

    logger.info("Werewolf Team wins!")
    return "Werewolf"


def get_voting_result(
    all_role_guesses_arr: List[List[str]],
) -> Tuple[List[str], List[float], List[int], List[int]]:
    """
    Creates confidence levels for each prediction and takes most
    common role guess array as the final guess for that index.
    guess_histogram stores counts of prediction arrays.
    wolf_votes stores individual votes for Wolves.
    """
    guess_histogram: Dict[Tuple[str, ...], int] = {}
    wolf_votes = [0] * const.NUM_PLAYERS
    vote_inds = []
    for i, prediction in enumerate(all_role_guesses_arr):
        pred_arr = tuple(prediction)
        if pred_arr in guess_histogram:
            guess_histogram[pred_arr] += 1
        else:
            guess_histogram[pred_arr] = 1
        vote_ind = get_player_vote(i, prediction)
        wolf_votes[vote_ind] += 1
        vote_inds.append(vote_ind)

    logger.info(f"\nVote Array: {wolf_votes}\n")
    assert sum(wolf_votes) == const.NUM_PLAYERS

    all_role_guesses, _ = max(guess_histogram.items(), key=lambda x: x[1])
    guessed_wolf_inds = [i for i, count in enumerate(wolf_votes) if count == max(wolf_votes)]

    confidence = []
    for i in range(const.NUM_ROLES):
        role_dict: Dict[str, int] = {role: 0 for role in const.ROLE_SET}
        for prediction in all_role_guesses_arr:
            role_dict[prediction[i]] += 1
        count = max(role_dict.values())
        confidence.append(count / const.NUM_PLAYERS)

    return list(all_role_guesses), confidence, guessed_wolf_inds, vote_inds


def get_player_vote(ind: int, prediction: List[str]) -> int:
    """ Updates Wolf votes for a given prediction. """
    no_wolves_guess = (ind + 1) % const.NUM_PLAYERS
    if const.IS_USER[ind]:
        logger.info(f"\nWhich Player is a Wolf? (Type {no_wolves_guess} if there are no Wolves)")
        return util.get_player(is_user=True)

    # TODO find the most likely Wolf and only vote for that one
    wolf_inds = util.find_all_player_indices(prediction, "Wolf")
    if wolf_inds:
        return random.choice(wolf_inds)

    # There are some really complicated game mechanics for the Minion.
    # https://boardgamegeek.com/thread/1422062/pointing-center-free-parking
    return no_wolves_guess
