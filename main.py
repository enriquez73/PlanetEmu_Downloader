from planet_emu_spider import PlanetemuSpider
import click

WEB = 'https://www.planetemu.net'
PLANETEMU = [
    # 'commodore-amiga-hardfiles-hdf',
    # 'commodore-amiga-games-adf',
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
    'nintendo-nintendo-entertainment-system',
    'mame-roms',
    # 'nec-pc-engine',
    # 'sony-playstation-games-europe',
    # 'panasonic-3do-interactive-multiplayer-games',  # No van en la raspberry PI
]

def run_spider(rom):
    print(f'Downloading from {WEB} ...')
    print(f'Downloading Roms for {rom} ...')
    url = f'/roms/{rom}'
    prefix = f'/rom/{rom}'
    spider = PlanetemuSpider(WEB, url, rom)
    spider.get_games(prefix)
    spider.download_skipped_games()


@click.command()
@click.option(
    "--rom", prompt="Local or remote",
    help="Where to upload files.",
    type=click.Choice(
        PLANETEMU,
        case_sensitive=False)
)
def destination_choice(rom):
    click.echo(rom)
    run_spider(rom)


if __name__ == '__main__':
    _config = destination_choice()
    # _config = 'config_remote.ini'
    # _config = 'config_local.ini'
    print(f'Ci passo {_config}')
    run_backup(_config)


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
