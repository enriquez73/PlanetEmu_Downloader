import json

import requests
from bs4 import BeautifulSoup


def urljoin(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    """

    return "/".join(map(lambda x: str(x.lstrip('/')).rstrip('/'), args))


BASE_URL = "https://www.planetemu.net"
url = urljoin(BASE_URL, 'roms/mame-roms/')
page = requests.get(url)

# print(page.text)

soup = BeautifulSoup(page.content, "html.parser")

anchors = soup.find_all('a')
mame_pages = []
for anchor in anchors:
    href = anchor.attrs.get('href')
    if href and '/rom/mame-roms/' in href:
        mame_pages.append(href)

'''
<a href="/rom/mame-roms/88games">
'88 Games </a>'''

php_page = 'https://www.planetemu.net/php/roms/download.php'
'''id: 
4004967
download: 
Télécharger'''
for mame in mame_pages:
    _url = urljoin(BASE_URL, mame)
    game_page = requests.get(_url)
    g_soup = BeautifulSoup(game_page.content, "html.parser")
    form = g_soup.find('form', class_='downloadForm')
    for el in form.find_all('input'):
        if el.attrs['name'] == 'id':
            _id = el.attrs['value']
        if el.attrs['name'] == 'download':
            _download = el.attrs['value']
    payload = {
        'id': _id,
        'download': _download,
    }
    resp = requests.post(php_page, json=payload, allow_redirects=True)
    head = resp.headers
    print(json.loads(head, ))

