from gensim.models import KeyedVectors
from pathlib import Path

import click

from yanr.decoder.decoder import Decoder, click_options


class Word2vec(Decoder):
    def __init__(self, model: str, source, destination, binary: bool = True):
        """Word2vec decoder

        Args:
            model (str): path to word2vec model
            source (str or dict or None): url/path, dict or None
            destination (str or dict or None): url/path, dict or None
            binary (bool): is model binary?
            https://rusvectores.org/ru/models/
            https://github.com/RaRe-Technologies/gensim-data

        Returns: dict or None
        """
        super().__init__(source=source, destination=destination)
        self.model = model
        self.binary = binary

    def __call__(self):
        d = self.load()
        p = Path(self.model)
        m = KeyedVectors.load_word2vec_format(p, binary=self.binary)
        for n in d['news']:
            n['title_decoding'] = ' '.join(
                m.index_to_key[x] if x != -1 else '<UNK>' for x in n['title_encoding'])
            n['text_decoding'] = ' '.join(
                m.index_to_key[x] if x != -1 else '<UNK>' for x in n['text_encoding'])
        return self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
@click.option('-m', '--model', help='unpack source if one is archive')
@click.option('--binary/--no-binary', default=True, help='is model binary?')
@click.pass_context
def word2vec_cli(ctx, model, source, destination, binary):
    # stemmer_kwargs = dict(x.split('=') for x in ctx.args if '=' in x)
    Word2vec(model, source, destination, binary)()


if __name__ == '__main__':
    word2vec_cli()
