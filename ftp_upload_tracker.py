from tqdm import tqdm


class FtpUploadTracker:
    size_written = 0
    total_size = 0
    last_shown_percent = 0

    def __init__(self, total_size, filename):
        self.total_size = total_size
        self.filename = filename
        self.bar = tqdm(
            desc=f'Uploading {filename[:30]}[...]',
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            colour='green'
            #  ncols=120,
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
