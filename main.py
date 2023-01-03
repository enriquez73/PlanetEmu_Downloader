import click
from enum import Enum

from planet_emu_spider import PlanetemuSpider
from utils import Choices, PROMPT


WEB = 'https://www.planetemu.net'


def run_spider(rom):
    print(f'Downloading from {WEB} ...')
    print(f'Downloading Roms for {rom} ...')
    url = f'/roms/{rom}'
    prefix = f'/rom/{rom}'
    spider = PlanetemuSpider(WEB, url, rom)
    spider.get_games(prefix)
    spider.download_skipped_games()


# _prompt = f'Roms: \n{Planet.A.name} - {Planet.A.value}\n{Planet.B.name} - {Planet.B.value}\n'

@click.command()
@click.option(
    "--rom", prompt=PROMPT,
    help="Where to upload files.",
    type=click.Choice(
        [d.name for d in Choices],
        case_sensitive=False)
)
def destination_choice(rom):
    click.echo(rom)
    chosen = Choices[rom].value
    print(chosen)
    run_spider(chosen)


if __name__ == '__main__':
    _config = destination_choice()
    # _config = 'config_remote.ini'
    # _config = 'config_local.ini'
    print(f'Ci passo {_config}')
    run_spider(_config)


# if __name__ == '__main__':
#     web = 'https://www.planetemu.net'
# 
#     print(f'Downloading from {web} ...')
# 
#     for rom in PLANETEMU:
#         print(f'Downloading Roms for {rom} ...')
#         url = f'/roms/{rom}'
#         prefix = f'/rom/{rom}'
#         spider = PlanetemuSpider(web, url, rom)
#         spider.get_games(prefix)
#         spider.download_skipped_games()
