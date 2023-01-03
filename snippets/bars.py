from enum import Enum

from tqdm import tqdm
from pathlib import Path
import time
import os

TARGET_PATH = Path(os.path.join('..', 'ROMS'))
rom_set = 'commodore-amiga-games-adf'
rom_set_sub_page = '0'
rom_name = '1943 - The Battle of Midway (1989)(GO!)[cr PNA].zip'

# target_len = len(os.listdir(str(TARGET_PATH)))
# bar = tqdm(range(target_len), position=0, leave=False, colour='green')
# for i in TARGET_PATH.iterdir():
#     bar.set_description(str(i), True)
#     for j in tqdm(range(10), position=1, desc="j", leave=False, colour='red', ncols=80):
#         time.sleep(0.3)
#     bar.update(1)
position = 0
# for a in tqdm(range(3), position=position, desc="a", leave=False, colour='red', ncols=80):
#     position += 1
#     for b in tqdm(range(3), position=position, desc="b", leave=False, colour='green', ncols=80):
#         # position += 1
#         for c in tqdm(range(3), position=position+1, desc="c", leave=False, colour='blue', ncols=80):
#             time.sleep(0.3)


bars = {}


class Colors(Enum):
    A = 'BLACK'
    B = 'RED'
    C = 'GREEN'
    D = 'BLUE'
    E = 'MAGENTA'


def upload(_bars, target_path, _position):

    # _bars = {**_bars, str(target_path): bar}
    for file in target_path.iterdir():
        name = str(file)
        parent = str(file.parent)
        color = Colors[chr(_position + 65)].value
        if file.is_dir():

            target_len = len(os.listdir(name))
            desc = f'[...]{name[-20:]}'
            bar = tqdm(
                range(target_len),
                desc=f'{_position}-{desc:>25}',
                position=_position,
                leave=False,
                colour=color
            )
            # print(str(file))
            _bars = {**_bars, name: bar}
            _bars[parent].update(1)
            upload(_bars, file, _position + 1)
        else:
            desc = f'[...]{name[-20:]}'
            for _j in tqdm(
                    range(len(name)//2),
                    position=_position,
                    desc=f'{_position}-{desc:>25}',
                    leave=False, colour=color
            ):
                time.sleep(0.01)
            _bars[parent].update(1)


_name = str(TARGET_PATH)
_target_len = len(os.listdir(_name))
_bar = tqdm(
    range(_target_len),
    desc=f'{position}-{_name}',
    position=position,
    leave=False,
    colour=Colors[chr(position+65)].value
)
bars = {**bars, str(TARGET_PATH): _bar}
upload(bars, TARGET_PATH, position + 1)
