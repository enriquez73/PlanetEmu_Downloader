import ssl

import requests
from bs4 import BeautifulSoup


def urljoin(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    """

    return "/".join(map(lambda x: str(x.lstrip('/')).rstrip('/'), args))


class Soup(object):
    def __call__(self, *args, **kwargs):
        _url = kwargs.get('url')

        # Ignora error de certificado SSL
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # html = urllib.request.urlopen(_url, context=ctx).read()
        html = requests.get(_url)
        return BeautifulSoup(html.content, 'html.parser')
