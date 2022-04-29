from urllib.request import urlopen
import shutil
# import requests
from pathlib import Path
from gzip import GzipFile
from zipfile import ZipFile
import tarfile
from io import BytesIO

import click

from yanr.base.base import Base, click_options


class Url(Base):
    def __init__(self,
                 source: str = 'example.com/data.txt',
                 destination: str = 'data.txt',
                 mode: str = 'urllib',
                 unpack: bool = True) -> None:
        """Base class for preprocessors

        Args:
            source (str): url
            destination (str): url or path to file
            mode (str): module to retrieve data (urllib or requests)
            unpack (bool): unpack source if one is archive

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.mode = mode
        self.unpack = unpack

    def __call__(self) -> None:
        """Load data from source and save to destination

        Returns: None
        """
        if '://' in self.destination:
            raise NotImplementedError('Url destination')
        else:
            p = Path(self.destination).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
        if self.mode == 'urllib':
            if self.unpack and self.source.endswith('tar.gz') \
                    or self.source.endswith('tgz'):
                p.mkdir(parents=True, exist_ok=True)
                with urlopen(self.source) as r:
                    with tarfile.open(name=None, fileobj=BytesIO(r.read())) as u:
                        print(u.getmembers())
                        u.extractall(p)
            elif self.unpack and self.source.endswith('.gz'):
                with urlopen(self.source) as r, open(p, 'wb') as f:
                    with GzipFile(fileobj=r) as u:
                        shutil.copyfileobj(u, f)
            elif self.unpack and self.source.endswith('.zip'):
                p.mkdir(parents=True, exist_ok=True)
                with urlopen(self.source) as r:
                    with ZipFile(BytesIO(r.read())) as u:
                        print(u.namelist())
                        u.extractall(p)
            else:
                with urlopen(self.source) as r, open(p, 'wb') as f:
                    shutil.copyfileobj(r, f)
        elif self.mode == 'requests':
            raise NotImplementedError(self.mode)
            # r = requests.get(self.source)
            # with open(p, 'wb') as f:
            #     f.write(r.content)
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
