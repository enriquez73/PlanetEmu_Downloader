from tqdm import tqdm
from utils import Colors


class FtpUploadTracker:
    size_written = 0
    total_size = 0
    last_shown_percent = 0

    def __init__(self, total_size, filename, position):
        color = Colors[chr(position + 65)].value
        self.total_size = total_size
        _filename = ''
        if len(filename) > 30:
            _filename = f'{filename[:30]}[...]'
        else:
            _filename = f'{filename}'
        self.bar = tqdm(
            desc='Uploading file: {:>35}'.format(_filename[:35]),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            colour=color,
            # ncols=120,
            position=position,
            leave=False
            # nrows=2,
        )

    def __exit__(self):
        self.bar.close()

    def handle(self, block):
        # self.size_written += len(block)
        self.bar.update(len(block))
        # percent_complete = round((self.size_written / self.total_size) * 100)
        #
        # if self.last_shown_percent != percent_complete:
        #     self.last_shown_percent = percent_complete
        #     print(f'Uploading {self.filename} - {str(percent_complete)}% complete \r', end='')
