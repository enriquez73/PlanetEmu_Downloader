import ssl

import requests
import os
from bs4 import BeautifulSoup
from aenum import Enum, extend_enum

BASE_DIR = os.path.join('.', 'ROMS')


def urljoin(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    """

    return "/".join(map(lambda x: str(x.lstrip('/')).rstrip('/'), args))


def get_files_in_directory(path):
    return os.listdir(path)


class Soup(object):
    def __call__(self, *args, **kwargs):
        _url = kwargs.get('url')

        # print('Requesting url: %s' % _url)
        # Ignora error de certificado SSL
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # html = urllib.request.urlopen(_url, context=ctx).read()
        html = requests.get(_url)
        # print(f'Requested url: {_url}')
        return BeautifulSoup(html.content, 'html.parser')


FTP_DESTINATION = [
    'local',
    'remote'
]


PLANETEMU = [
    'commodore-amiga-hardfiles-hdf',
    'commodore-amiga-games-adf',
    'atari-2600',
    'atari-5200',
    'atari-7800',
    'coleco-colecovision',
    'sega-game-gear',
    'mattel-intellivision',
    'atari-jaguar',
    'atari-lynx',
    'sega-master-system',
    'sega-mega-drive',
    'snk-neo-geo-pocket',
    'snk-neo-geo-cd-world',
    'nintendo-nintendo-entertainment-system',
    'mame-roms',
    'nec-pc-engine',
    'sony-playstation-games-europe',
    'panasonic-3do-interactive-multiplayer-games',  # No van en la raspberry PI
]

PROMPT = f'Roms: \n'
_PROMPT = [f'{chr(65 + idx)} - {value}\n' for idx, value in enumerate(PLANETEMU)]
for s in _PROMPT:
    PROMPT += s


PROMPT_FTP = f'Roms: \n'
_PROMPT_FTP = [f'{chr(65 + idx)} - {value}\n' for idx, value in enumerate(FTP_DESTINATION)]
for s in _PROMPT_FTP:
    PROMPT_FTP += s


class Choices(Enum):
    _init_ = 'value __doc__'


for idx, value in enumerate(PLANETEMU):
    extend_enum(Choices, chr(65 + idx), value, '')


class ChoicesFtp(Enum):
    _init_ = 'value __doc__'


for idx, value in enumerate(FTP_DESTINATION):
    extend_enum(ChoicesFtp, chr(65 + idx), value, '')
