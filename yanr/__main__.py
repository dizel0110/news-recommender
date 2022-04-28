import click

from yanr.preprocessor import Stemmer, stemmer_cli
from yanr.parser import Habr, habr_cli, News3d, news3d_cli, Ibrae, ibrae_cli

cls2cli = {
    Stemmer.__name__: stemmer_cli,
    Habr.__name__: habr_cli,
    News3d.__name__: news3d_cli,
    Ibrae.__name__: ibrae_cli,
}


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click.argument('cls')
def cli(cls):
    return cls2cli[cls]()


if __name__ == '__main__':
    cli()
