#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Juhegue
# jue abr 23 08:29:55 CEST 2020

import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

import requests
import urllib3
from bs4 import BeautifulSoup
from tqdm import tqdm

from planet_emu_spider import PlanetemuSpider

PLANETEMU = [
    # 'atari-2600',
    # 'atari-5200',
    # 'atari-7800',
    # 'coleco-colecovision',
    # 'sega-game-gear',
    # 'mattel-intellivision',
    # 'atari-jaguar',
    # 'atari-lynx',
    # 'sega-master-system',
    # 'sega-mega-drive',
    # 'snk-neo-geo-pocket',
    # 'snk-neo-geo-cd-world',
    'mame-roms',
    # 'nec-pc-engine',
    # 'sony-playstation-games-europe',
    # 'panasonic-3do-interactive-multiplayer-games',  # No van en la raspberry PI
]


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


if __name__ == '__main__':
    web = 'https://www.planetemu.net'

    for rom in PLANETEMU:

        url = f'/roms/{rom}'
        prefix = f'/rom/{rom}'
        spider = PlanetemuSpider(web, url, rom)
        spider.get_games(prefix)
        print(spider.pages)

        # if not spider(web, url, sufijo, rom):
        #     break
