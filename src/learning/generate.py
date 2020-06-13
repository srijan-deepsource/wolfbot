"""
generate.py
To run, cd to src/ and run python -m learning.generate
"""
import json
import time

from src import const
from src.const import logger
from src.encoder import WolfBotEncoder
from src.one_night import play_one_night_werewolf


def generate_data() -> None:
    """ Simulate games and store data in simulations folder. """
    weights = [3 ** i for i in range(1, const.NUM_PLAYERS + 1)]
    sim_list = []
    logger.set_level(0)
    for i, weight in enumerate(weights):
        const.FIXED_WOLF_INDEX = i
        logger.warning(f"Computing index: {i}")
        for _ in range(weight):
            simulation = play_one_night_werewolf(save_replay=False)
            sim_list.append(simulation)

    fname = f"learning/simulations/simulation_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f_sim:
        json.dump(sim_list, f_sim, cls=WolfBotEncoder)


if __name__ == "__main__":
    generate_data()
