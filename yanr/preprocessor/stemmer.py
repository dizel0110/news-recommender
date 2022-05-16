import nltk.stem as stem
from typing import Optional, Dict

import click

from yanr.preprocessor.preprocessor import Preprocessor, click_options


class Stemmer(Preprocessor):
    def __init__(self, source, destination, stemmer: str = 'PorterStemmer',
                 stemmer_kwargs: Optional[Dict] = None):
        """Stemmer

        Args:
            source (str or dict or None): url/path, dict or None
            destination (str or dict or None): url/path, dict or None
            stemmer (str): class name of the stemmer
                (see https://www.nltk.org/api/nltk.stem.html)
            stemmer_kwargs (dict, optional): keyword arguments of stemmer

        Returns: dict or None
        """
        super().__init__(source=source, destination=destination)
        self.stemmer = stemmer
        self.stemmer_kwargs = {} if stemmer_kwargs is None else stemmer_kwargs

    def __call__(self):
        d = self.load()
        s = getattr(stem, self.stemmer)(**self.stemmer_kwargs)
        fields = ['title', 'text']
        preprocessed_fields = [f'preprocessed_{x}' for x in fields]
        for f, pf in zip(fields, preprocessed_fields):
            for n in d['news']:
                source_field = pf if pf in n else f
                n[pf] = ' '.join(s.stem(x.strip()) for x in n[source_field].split())
        return self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
@click.option('--stemmer', default='PorterStemmer',
              help='stemmer class name (see https://www.nltk.org/api/nltk.stem.html)')
@click.pass_context
def stemmer_cli(ctx, source, destination, stemmer):
    stemmer_kwargs = dict(x.split('=') for x in ctx.args if '=' in x)
    Stemmer(source, destination, stemmer, stemmer_kwargs)()


if __name__ == '__main__':
    stemmer_cli()
