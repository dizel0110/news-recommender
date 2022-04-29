import string

import click

from yanr.preprocessor.preprocessor import Preprocessor, click_options


class Cleaner(Preprocessor):
    def __init__(self, source: str, destination: str, punctuation: bool = True) -> None:
        """Text cleaner

        Args:
            source (str): url or path to file
            destination (str): url or path to file
            punctuation (bool): remove punctuation

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.punctuation = punctuation

    def __call__(self) -> None:
        """Clean text

        Returns: None
        """
        d = self.load()
        fields = ['title', 'text']
        preprocessed_fields = [f'preprocessed_{x}' for x in fields]
        for f, pf in zip(fields, preprocessed_fields):
            for n in d['news']:
                source_field = pf if pf in n else f
                if self.punctuation:
                    n[pf] = n[source_field].translate(
                        str.maketrans('', '', string.punctuation))
        self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
@click.option('--punctuation/--no-punctuation', default=True,
              help='remove punctuation')
@click.pass_context
def cleaner_cli(ctx, source, destination, punctuation):
    Cleaner(source, destination, punctuation)()


if __name__ == '__main__':
    cleaner_cli()
