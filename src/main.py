''' main.py '''
import time

from src.stats import Statistics
from src.one_night import play_one_night_werewolf
from src.const import logger
from src import const

def main(save_replay: bool = True) -> None:
    ''' Simulate play_one_night_werewolf and create a Statistics instance for the runs. '''
    start_time = time.time()
    stats = Statistics()
    for num in range(const.NUM_GAMES):
        if const.SHOW_PROGRESS and num % 10 == 0:
            logger.warning(f'Currently on Game: {num}')
        game_result = play_one_night_werewolf(save_replay)
        stats.add_result(game_result)
    stats.print_statistics()
    logger.warning(f'\nTime taken: {time.time() - start_time}')


if __name__ == '__main__':
    main(const.SAVE_REPLAY)
