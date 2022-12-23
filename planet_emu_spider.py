import os
import re
import time

import requests
import urllib3
from tqdm import tqdm

import utils as u
from utils import Soup, urljoin, get_files_in_directory

SLEEP_TIME = 1.5
BASE_DIR = u.BASE_DIR


def get_games_in_page(_web, page_url, prefix):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    suop = Soup()
    sopa = suop(url=_web + page_url)
    tags = sopa('a')
    games = []
    for tag in tags:
        href = tag.get('href', None)
        if href and href.startswith(prefix):
            games.append(href)
    return games


def create_directory(path):
    if not os.path.isdir(path):
        os.mkdir(path)


class PlanetemuSpider(object):
    def __init__(self, _web, _url, rom_name):
        print('Initializing spider for %s' % rom_name)
        self.base_url = _web
        self.rom_name = rom_name
        create_directory(self.rom_name)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        suop = Soup()
        sopa = suop(url=_web + _url)
        tags = sopa('a')
        self.pages = []
        self.skipped = []
        for tag in tags:
            href = tag.get('href', None)
            if href and href.startswith(_url + '?page='):
                if href not in self.pages:
                    self.pages.append(href)

    def get_games(self, prefix):
        for page in self.pages:
            page_name = page.split('=')[1]
            games = get_games_in_page(self.base_url, page, prefix)
            games_number = len(games)
            dest_path = os.path.join(BASE_DIR, self.rom_name, page_name)
            create_directory(dest_path)

            games_in_dir = get_files_in_directory(dest_path)

            for idx, g in enumerate(games):
                file_name = g.split('/')[-1] + '.zip'
                if file_name not in games_in_dir:
                    res = self.download_game(g, idx, games_number, page_name)
                    time.sleep(SLEEP_TIME)
                    if not res:
                        break
                else:
                    print(f'Skipping {str(file_name)}: already present in {dest_path}')

    def download_skipped_games(self):
        index = 0
        games_number = len(self.skipped)
        while len(self.skipped) > 0:
            game_url = self.skipped.pop()
            self.download_game(game_url, index, games_number, 'skipped')
            index += 1

    def download_game(self, game_url, idx, games_number, page_name=''):
        dest_path = os.path.join(BASE_DIR, self.rom_name, page_name)
        fname = ''
        try:
            s = Soup()
            download_url = urljoin(self.base_url, game_url)
            sopa = s(url=download_url)
            action = sopa.find('form', {'name': 'MyForm'}).get('action')
            _id = sopa.find('input', {'name': 'id'}).get('value')
            download = sopa.find('input', {'name': 'download'}).get('value')

            data = {
                'id': _id,
                'download': download,
            }
            form = self.base_url + action
            with requests.post(form, data=data, verify=False, stream=True) as response:
                response.raise_for_status()
                content = response.headers.get('content-disposition')

                name = None
                if content:
                    name = re.findall("filename=(.+)", content)
                    if name:
                        name = name[0].replace('"', '')

                if not name:
                    name = game_url.split('/')[-1] + '.zip'

                fname = os.path.join(dest_path, name)
                self.download_write(fname, games_number, idx, name, page_name, response)
                return True
        except KeyboardInterrupt:
            if fname:
                os.remove(fname)
            return False
        except Exception as e:
            if fname:
                os.remove(fname)
            print(f'Skipping: ERROR {e}')
            if download_url not in self.skipped:
                self.skipped.append(download_url)
            return True

    def download_write(self, fname, games_number, idx, name, page_name, response):
        if not os.path.isfile(fname):
            total = int(response.headers.get('content-length', 0))
            # Can also replace 'file' with an io.BytesIO object
            description = f'[({page_name}) - {idx:04d}/{games_number:04d}] - {name:20s}'
            with open(fname, 'wb') as file, tqdm(
                    desc=description,
                    total=total,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                    #  ncols=120,
                    nrows=2,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)
        else:
            print(f'Skipping: [{page_name} - {idx:03d}-{games_number:03d}] - {name:15s}: Already downloaded')

    # def __call__(self, _web, _url, _sufijo, path):
    #     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #
    #     suop = Soup()
    #     sopa = suop(url=_web + _url)
    #     hrefs = []
    #     for tag in sopa('a'):
    #         href = tag.get('href', None)
    #         if href and href.startswith(_sufijo):
    #             hrefs.append(href)
    #
    #     for n, href in enumerate(hrefs):
    #         time.sleep(1.5)            # print('[{:03d}-{:03d}]{}'.format(len(hrefs), n, href), end='')
    #         fname = None
    #         try:
    #             sopa = suop(url=_web + href)
    #             action = sopa.find('form', {'name': 'MyForm'}).get('action')
    #             _id = sopa.find('input', {'name': 'id'}).get('value')
    #             download = sopa.find('input', {'name': 'download'}).get('value')
    #
    #             data = {
    #                 'id': _id,
    #                 'download': download,
    #             }
    #             form = _web + action
    #             with requests.post(form, data=data, verify=False, stream=True) as response:
    #                 response.raise_for_status()
    #                 content = response.headers.get('content-disposition')
    #
    #                 name = None
    #                 if content:
    #                     name = re.findall("filename=(.+)", content)
    #                     if name:
    #                         name = name[0].replace('"', '')
    #
    #                 if not name:
    #                     name = href.split('/')[-1] + '.zip'
    #
    #                 fname = os.path.join(path, name)
    #                 if not os.path.isfile(fname):
    #                     total = int(response.headers.get('content-length', 0))
    #                     # Can also replace 'file' with a io.BytesIO object
    #                     description = 'Downloading: [{:03d}-{:03d}]{}'.format(len(hrefs), n, href)
    #                     with open(fname, 'wb') as file, tqdm(
    #                             desc=description,
    #                             total=total,
    #                             unit='iB',
    #                             unit_scale=True,
    #                             unit_divisor=1024,
    #                     ) as bar:
    #                         for data in response.iter_content(chunk_size=1024):
    #                             size = file.write(data)
    #                             bar.update(size)
    #
    #                     # with open(fname, 'wb') as f:
    #                     #     size = len(response.content)
    #                     #     description = 'Downloading: [{:03d}-{:03d}]{}'.format(len(hrefs), n, href)
    #                     #     for chunk in response.iter_content(chunk_size=10240):
    #                     #         if chunk:
    #                     #             f.write(chunk)
    #
    #                 # print(':', name)
    #         except KeyboardInterrupt:
    #             if fname:
    #                 os.remove(fname)
    #             return False
    #         except Exception as e:
    #             if fname:
    #                 os.remove(fname)
    #             print(f': ERROR {e}')
    #
    #     return True
