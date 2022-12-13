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

if __name__ == '__main__':
    web = 'https://www.planetemu.net'

    print(f'Downloading from {web} ...')

    for rom in PLANETEMU:
        print(f'Downloading Roms for {rom} ...')
        url = f'/roms/{rom}'
        prefix = f'/rom/{rom}'
        spider = PlanetemuSpider(web, url, rom)
        spider.get_games(prefix)
        spider.download_skipped_games()
