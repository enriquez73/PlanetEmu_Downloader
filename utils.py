import ssl
import requests
import os
import json

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
PLANETEMU = []

with open('config.json', 'r') as f:
    config = json.load(f)
    PLANETEMU = config['PLANETEMU']

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


class Colors(Enum):
    A = 'YELLOW'
    B = 'RED'
    C = 'GREEN'
    D = 'BLUE'
    E = 'MAGENTA'
