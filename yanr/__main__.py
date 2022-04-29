import click

from yanr.getter import Url, url_cli
from yanr.parser import Habr, habr_cli, News3d, news3d_cli, Ibrae, ibrae_cli
from yanr.preprocessor import Stemmer, stemmer_cli, Morpher, morpher_cli, \
    Cleaner, cleaner_cli
from yanr.encoder import Word2vec as EncoderWord2vec
from yanr.encoder import word2vec_cli as encoder_word2vec_cli
from yanr.decoder import Word2vec as DecoderWord2vec
from yanr.decoder import word2vec_cli as decoder_word2vec_cli
from yanr.model import Word2vec, word2vec_cli
from yanr.postprocessor import Comparator, comparator_cli

cls2cli = {
    Cleaner.__name__.lower(): cleaner_cli,
    Comparator.__name__.lower(): comparator_cli,
    Habr.__name__.lower(): habr_cli,
    Ibrae.__name__.lower(): ibrae_cli,
    Morpher.__name__.lower(): morpher_cli,
    News3d.__name__.lower(): news3d_cli,
    Stemmer.__name__.lower(): stemmer_cli,
    Url.__name__.lower(): url_cli,
    Word2vec.__name__.lower(): word2vec_cli,
    f'encoder.{EncoderWord2vec.__name__.lower()}': encoder_word2vec_cli,
    f'decoder.{DecoderWord2vec.__name__.lower()}': decoder_word2vec_cli,
}


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click.argument('cls')
def cli(cls):
    return cls2cli[cls]()


if __name__ == '__main__':
    cli()
