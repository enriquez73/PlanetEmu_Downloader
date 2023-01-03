import json
import os
import posixpath
import shutil

from tqdm import tqdm
import click

from datetime import datetime
from ftplib import FTP
from pathlib import Path
from dateutil import parser

from ftp_upload_tracker import FtpUploadTracker
import utils as u


SUCCESS = 'Success'
ERROR = 'Error'
SKIPPED = 'Skipped'


class FtpUtils:
    def __init__(self, destination: str):

        self.current_local_path = None
        with open('config.json', 'r') as f:
            ftp_config = json.load(f)

        ftp_config = ftp_config[f'FTP_{destination.upper()}']

        self.ftp_url = ftp_config['FTP_URL']
        self.ftp_username = ftp_config['FTP_USER']
        self.ftp_password = ftp_config['FTP_PASSWORD']
        self.remote_dir = ftp_config['REMOTE_DIR']
        self.file_list = []
        self.skipped = []
        self.session = None
        self.connect()

    def connect(self):
        try:
            ftp_server = FTP()
            ftp_server.connect(self.ftp_url)
            ftp_server.login(self.ftp_username, self.ftp_password)

        except Exception as e:
            print(e)
        self.session = ftp_server
        self.check_or_create_remote_dir(self.remote_dir)
        self.current_local_path = Path('./ROMS')

    def create_remote_dir(self, _dir):
        try:
            self.session.cwd(_dir)
        except Exception as e:
            print(f'\n\n[create_remote_dir] - Exception occurred: {e}')
            self.session.mkd(_dir)
            self.session.cwd(_dir)

    def check_or_create_remote_dir(self, remote_dir):
        try:
            self.session.cwd(remote_dir)
            return f'Remote directory {remote_dir} already exists'
        except Exception as e:
            print(f'\n\n[check_or_create_remote_dir] - Exception occurred: {e}')
            if e.startswith('ConnectionAbortedError'):
                self.connect()

            _paths = remote_dir.split('/')
            _paths[0] = '/'

            for _path in _paths:
                self.create_remote_dir(_path)

            return f'Remote directory {remote_dir} created successfully'

    def current(self):
        return self.session.pwd()

    def is_dir(self, name, orignal_dir):
        try:
            self.session.cwd(name)
            self.session.cwd(orignal_dir)
            return True
        except Exception:
            return False

    def ls(self, backup_folder):
        self.session.cwd(backup_folder)
        contents = self.session.nlst()
        orignal_dir = self.current()
        files = [
            content
            for content in contents
            if not self.is_dir(content, orignal_dir)
        ]
        self.session.cwd('/')
        return files

    def mkdir(self, folder):
        self.session.mkd(folder)

    def is_file_uploadable(self, remote, file):
        file_absolute = str(file.absolute())
        local_file_size = int(os.path.getsize(file_absolute))
        uploadable = True
        file_list = []
        self.session.cwd(remote)

        file_list_names = self.session.nlst()
        file_list_names = [fn for fn in file_list_names if fn not in ['.', '..']]

        self.session.retrlines('LIST', file_list.append)
        file_list = [f for f in file_list if not f.startswith('d')]
        present = file.name in file_list_names
        return (
            next(
                (
                    self.check_date_and_size(
                        file, file_absolute, local_file_size
                    )
                    for f in file_list
                    if file.name in f
                ),
                (uploadable, local_file_size),
            )
            if present
            else (True, local_file_size)
        )

    def check_date_and_size(self, file, file_absolute, local_file_size):
        remote_ts = self.session.voidcmd(f'MDTM {file.name}')[4:].strip()
        remote_file_time = parser.parse(remote_ts)

        local_file_time = datetime.fromtimestamp(os.path.getmtime(file_absolute))
        uploadable = local_file_time > remote_file_time
        remote_file_size = self.session.size(file.name)

        uploadable = uploadable or (local_file_size > remote_file_size)
        return uploadable, local_file_size

    def sender(self, backup_folder, upload_file, position):
        _file = str(upload_file.absolute())
        remote_destination = f'{backup_folder}/{upload_file.name}'
        # print(f'Uploading {_file} to {remote_destination}', end='')
        uploadable, size = self.is_file_uploadable(backup_folder, upload_file)
        if uploadable:
            try:
                with open(_file, 'rb') as fd:
                    tracker = FtpUploadTracker(int(size), upload_file.name, position)
                    self.session.storbinary(f'STOR {remote_destination}', fd, 1024,
                                            callback=tracker.handle)
                    tracker.__exit__()
                return SUCCESS
            except Exception as e:
                print(f'\n\n[check_date_and_size] - Exception occurred: {e}')
                return ERROR
        else:
            return f'{SKIPPED} - {upload_file.name} already present'

    def remove(self, backup_folder, file):
        self.session.delete(f'{backup_folder}/{file}')

    def close_session(self):
        self.session.close()
        # self.session.quit()

    def destination_path(self, current_file):
        remote_tmp = str(current_file.absolute()).replace(str(self.current_local_path.absolute()), '')
        if remote_tmp.startswith('\\') or remote_tmp.startswith('/'):
            remote_tmp = remote_tmp[1:]
        remote_tmp = os.path.join(self.remote_dir, remote_tmp)
        return remote_tmp.replace(os.sep, posixpath.sep)

    def upload(self, _bars, target_path, _position):
        for file in target_path.iterdir():
            name = str(file)
            parent = str(file.parent)
            color = u.Colors[chr(_position + 65)].value
            if file.is_dir():
                destination_path = self.destination_path(file)
                result = self.check_or_create_remote_dir(destination_path)
                target_len = len(os.listdir(name))
                desc = f'[...]{name[-35:]}'
                bar = tqdm(
                    range(target_len),
                    desc='Processing dir: {:>35}'.format(desc),
                    position=_position,
                    leave=False,
                    colour=color
                )
                # print(str(file))
                _bars = {**_bars, name: bar}
                _bars[parent].update(1)
                self.upload(_bars, file, _position + 1)
                if len(os.listdir(file)) == 0:
                    try:
                        os.remove(file)
                    except OSError as e:
                        # print(f'\n\nException occurred: {e}')
                        pass

            else:
                response = self.sender(self.session.pwd(), file, _position)
                _bars[parent].update(1)
                if response == SUCCESS or response.startswith(SKIPPED):
                    local_destination_path = name.replace(str(Path(u.BASE_DIR)), 'UPLOADED')
                    parent_path = str(Path(local_destination_path).parent)
                    if not os.path.exists(parent_path):
                        os.makedirs(parent_path)
                    if os.path.exists(name):
                        shutil.move(name, local_destination_path)
                    if response.startswith(SKIPPED):
                        self.skipped.append(name)


def run_backup(_config):
    position = 0
    bars = {}
    ftp = FtpUtils(_config)
    target = Path(u.BASE_DIR)
    _name = str(target)
    _target_len = len(os.listdir(_name))
    desc = f'[...]{_name[-35:]}'
    _bar = tqdm(
        range(_target_len),
        desc='Processing dir: {:>35}'.format(desc),
        position=position,
        leave=False,
        colour=u.Colors[chr(position + 65)].value
    )
    bars = {**bars, _name: _bar}
    ftp.upload(bars, target, position + 1)
    # ftp.upload(Path(u.BASE_DIR))
    ftp.close_session()
    print('ALL DONE')
    for skip in ftp.skipped:
        print(f'Skipped: {skip}')


@click.command()
@click.option(
    "--config", prompt=u.PROMPT_FTP,
    help="Where to upload files.",
    type=click.Choice(
        [d.name for d in u.ChoicesFtp],
        case_sensitive=False)
)
def destination_choice(config):
    click.echo(config)
    chosen = u.ChoicesFtp[config].value
    print(chosen)

    print(f'Your choice: {chosen}')
    run_backup(chosen)


if __name__ == '__main__':
    _config = destination_choice()
    # _config = 'config_remote.ini'
    # _config = 'config_local.ini'
    print(f'Ci passo {_config}')
    run_backup(_config)
