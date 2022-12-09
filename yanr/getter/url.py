from urllib.request import urlopen
import shutil
# import requests
from pathlib import Path
import gzip
from zipfile import ZipFile
import tarfile
from io import BytesIO

import click

from yanr.getter.getter import Getter, click_options


class Url(Getter):
    def __init__(self, source: str, destination: str, mode: str = 'urllib',
                 unpack: bool = True):
        """Get data from url

        Args:
            source (str): url or path to file
            destination (str): url or path to file
            mode (str): module to retrieve data (urllib or requests)
            unpack (bool): unpack source if one is archive

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.mode = mode
        self.unpack = unpack

    def __call__(self):
        try:
            source_path = Path(self.source).resolve()
            is_local = source_path.exists()
        except Exception:
            is_local = False
        if '://' in self.destination:
            raise NotImplementedError('Url destination')
        else:
            p = Path(self.destination).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
        if self.mode == 'urllib':
            if self.unpack and self.source.endswith('tar.gz') \
                    or self.source.endswith('tgz'):
                p.mkdir(parents=True, exist_ok=True)
                if is_local:
                    with tarfile.open(self.source) as u:
                        
                        import os
                        
                        def is_within_directory(directory, target):
                            
                            abs_directory = os.path.abspath(directory)
                            abs_target = os.path.abspath(target)
                        
                            prefix = os.path.commonprefix([abs_directory, abs_target])
                            
                            return prefix == abs_directory
                        
                        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                        
                            for member in tar.getmembers():
                                member_path = os.path.join(path, member.name)
                                if not is_within_directory(path, member_path):
                                    raise Exception("Attempted Path Traversal in Tar File")
                        
                            tar.extractall(path, members, numeric_owner=numeric_owner) 
                            
                        
                        safe_extract(u, p)
                else:
                    with urlopen(self.source) as r:
                        with tarfile.open(name=None, fileobj=BytesIO(r.read())) as u:
                            u.extractall(p)
            elif self.unpack and self.source.endswith('.gz'):
                if is_local:
                    # https://stackoverflow.com/questions/31028815/how-to-unzip-gz-file-using-python
                    with gzip.open(self.source, 'rb') as fi:
                        with open(p, 'wb') as fo:
                            shutil.copyfileobj(fi, fo)
                else:
                    with urlopen(self.source) as r, open(p, 'wb') as f:
                        with gzip.GzipFile(fileobj=r) as u:
                            shutil.copyfileobj(u, f)
            elif self.unpack and self.source.endswith('.zip'):
                p.mkdir(parents=True, exist_ok=True)
                if is_local:
                    with ZipFile(self.source) as u:
                        u.extractall(p)
                else:
                    with urlopen(self.source) as r:
                        with ZipFile(BytesIO(r.read())) as u:
                            u.extractall(p)
            else:
                if is_local:
                    shutil.copy(self.source, p)
                else:
                    with urlopen(self.source) as r, open(p, 'wb') as f:
                        shutil.copyfileobj(r, f)
        elif self.mode == 'requests':
            raise NotImplementedError(self.mode)
        else:
            raise ValueError(self.mode)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
@click.option('--mode', default='urllib',
              help='module to retrieve data (urllib or requests)')
@click.option('--unpack/--no-unpack', default=True,
              help='unpack source if one is archive')
@click.pass_context
def url_cli(ctx, source, destination, mode, unpack):
    Url(source, destination, mode, unpack)()


if __name__ == '__main__':
    url_cli()
