import click

from yanr.preprocessor import Stemmer, stemmer_cli, Morpher, morpher_cli, \
    Cleaner, cleaner_cli
from yanr.parser import Habr, habr_cli, News3d, news3d_cli, Ibrae, ibrae_cli
from yanr.encoder import Word2vec, word2vec_cli
from yanr.url import Url, url_cli

cls2cli = {
    Cleaner.__name__: cleaner_cli,
    Habr.__name__: habr_cli,
    Ibrae.__name__: ibrae_cli,
    Morpher.__name__: morpher_cli,
    News3d.__name__: news3d_cli,
    Stemmer.__name__: stemmer_cli,
    Url.__name__: url_cli,
    Word2vec.__name__: word2vec_cli,
}


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click.argument('cls')
def cli(cls):
    return cls2cli[cls]()


if __name__ == '__main__':
    cli()
