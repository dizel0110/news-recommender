from gensim.models import KeyedVectors
from pathlib import Path

import click

from yanr.encoder.encoder import Encoder, click_options


class Word2vec(Encoder):
    def __init__(self, model: str, source: str, destination: str,
                 binary: bool = True) -> None:
        """Word2vec encoder

        Args:
            model (str): path to word2vec model
            source (str): url to database or path to file
            destination (str): url to database or path to file
            binary (bool): is model binary?
            https://rusvectores.org/ru/models/
            https://github.com/RaRe-Technologies/gensim-data

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.model = model
        self.binary = binary

    def __call__(self) -> None:
        """Make text encodings

        Returns: None
        """
        d = self.load()
        p = Path(self.model)
        m = KeyedVectors.load_word2vec_format(p, binary=self.binary)
        for n in d['news']:
            n['title_encoding'] = [m.key_to_index.get(x.strip(), -1)
                                   for x in n['preprocessed_title'].split()]
            n['text_encoding'] = [m.key_to_index.get(x.strip(), -1)
                                  for x in n['preprocessed_text'].split()]
        self.save(d)


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
