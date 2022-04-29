import nltk.stem as stem
from typing import Optional, Dict

import click

from yanr.preprocessor.preprocessor import Preprocessor, click_options


class Stemmer(Preprocessor):
    def __init__(self, source: str, destination: str, stemmer: str = 'PorterStemmer',
                 stemmer_kwargs: Optional[Dict] = None) -> None:
        """Stemmer

        Args:
            source (str): url to database or path to file
            destination (str): url to database or path to file
            stemmer (str): class name of the stemmer
                (see https://www.nltk.org/api/nltk.stem.html)
            stemmer_kwargs (dict, optional): keyword arguments of stemmer

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.stemmer = stemmer
        self.stemmer_kwargs = {} if stemmer_kwargs is None else stemmer_kwargs

    def __call__(self) -> None:
        """Stem text

        Returns: None
        """
        d = self.load()
        s = getattr(stem, self.stemmer)(**self.stemmer_kwargs)
        for n in d['news']:
            n['title'] = ' '.join(s.stem(x.strip()) for x in n['title'].split())
            n['text'] = ' '.join(s.stem(x.strip()) for x in n['text'].split())
        self.save(d)


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
