import json
import os
import posixpath

import click

from datetime import datetime
from ftplib import FTP
from pathlib import Path
from dateutil import parser

from ftp_upload_tracker import FtpUploadTracker
import utils as u


class FtpUtils:
    def __init__(self, destination):

        with open(destination, 'r') as f:
            ftp_config = json.load(f)

        ftp_config = ftp_config['FTP']

        self.ftp_url = ftp_config['FTP_URL']
        self.ftp_username = ftp_config['FTP_USER']
        self.ftp_password = ftp_config['FTP_PASSWORD']
        self.remote_dir = ftp_config['REMOTE_DIR']
        self.file_list = []

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
            print(e)
            self.session.mkd(_dir)
            self.session.cwd(_dir)

    def check_or_create_remote_dir(self, remote_dir):
        try:
            self.session.cwd(remote_dir)
            return f'Remote directory {remote_dir} already exists'
        except Exception as e:
            print(e)
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
        file_list_names = []
        self.session.cwd(remote)

        file_list_names = self.session.nlst()
        file_list_names = [fn for fn in file_list_names if fn != '.' and fn != '..']

        self.session.retrlines('LIST', file_list.append)
        file_list = [f for f in file_list if not f.startswith('d')]
        present = file.name in file_list_names
        if not present:
            return True, local_file_size
        else:
            for f in file_list:
                if file.name in f:
                    remote_ts = self.session.voidcmd(f'MDTM {file.name}')[4:].strip()
                    remote_file_time = parser.parse(remote_ts)

                    local_file_time = datetime.fromtimestamp(os.path.getmtime(file_absolute))
                    uploadable = local_file_time > remote_file_time
                    remote_file_size = self.session.size(file.name)

                    uploadable = uploadable or (local_file_size > remote_file_size)
                    return uploadable, local_file_size
        return uploadable, local_file_size

    def sender(self, backup_folder, upload_file):
        _file = str(upload_file.absolute())
        remote_destination = f'{backup_folder}/{upload_file.name}'
        # print(f'Uploading {_file} to {remote_destination}', end='')
        uploadable, size = self.is_file_uploadable(backup_folder, upload_file)
        if uploadable:
            try:
                with open(_file, 'rb') as fd:
                    tracker = FtpUploadTracker(int(size), upload_file.name)
                    self.session.storbinary(f'STOR {remote_destination}', fd, 1024,
                                            callback=tracker.handle)
                    tracker.__exit__()
            except Exception as e:
                print('')
                print(f'Exception occurred: {e}')
        else:
            print(f'{upload_file.name} already present - skipping')

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

    def upload(self, target_path):
        for file in target_path.iterdir():
            if file.is_dir():
                destination_path = self.destination_path(file)
                result = self.check_or_create_remote_dir(destination_path)
                print(result)
                self.upload(file)
            else:
                self.sender(self.session.pwd(), file)


def run_backup(_config):
    ftp = FtpUtils(_config)
    ftp.upload(Path(u.BASE_DIR))
    ftp.close_session()


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
    run_backup(f'config_{chosen}.json')


if __name__ == '__main__':
    _config = destination_choice()
    # _config = 'config_remote.ini'
    # _config = 'config_local.ini'
    print(f'Ci passo {_config}')
    run_backup(_config)
