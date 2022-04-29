import pymorphy2
from typing import Optional, Dict

import click

from yanr.preprocessor.preprocessor import Preprocessor, click_options


class Morpher(Preprocessor):
    def __init__(self, source: str, destination: str,
                 morpher_kwargs: Optional[Dict] = None) -> None:
        """Morpher analyzer

        Args:
            source (str): url or path to file
            destination (str): url or path to file
            morpher_kwargs (dict, optional): keyword arguments of MorphAnalyzer
                (see https://pymorphy2.readthedocs.io/en/stable/misc/api_reference.html)

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.morpher_kwargs = {} if morpher_kwargs is None else morpher_kwargs

    def __call__(self) -> None:
        """Lemmatize and add universal POS tag to words

        Returns: None
        """
        d = self.load()
        m = pymorphy2.MorphAnalyzer(**self.morpher_kwargs)
        fields = ['title', 'text']
        preprocessed_fields = [f'preprocessed_{x}' for x in fields]
        for f, pf in zip(fields, preprocessed_fields):
            for n in d['news']:
                source_field = pf if pf in n else f
                n[pf] = ' '.join(
                    f'{x.normal_form}_{x.tag.POS}'
                    for x in [m.parse(y.strip())[0] for y in n[source_field].split()])
        self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
@click.pass_context
def morpher_cli(ctx, source, destination):
    morpher_kwargs = dict(x.split('=') for x in ctx.args if '=' in x)
    Morpher(source, destination, morpher_kwargs)()


if __name__ == '__main__':
    morpher_cli()
