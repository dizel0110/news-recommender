import string

import click

from yanr.preprocessor.preprocessor import Preprocessor, click_options


class Cleaner(Preprocessor):
    def __init__(self, source, destination, punctuation: bool = True):
        """Text cleaner

        Args:
            source (str or dict or None): url/path, dict or None
            destination (str or dict or None): url/path, dict or None
            punctuation (bool): remove punctuation

        Returns: dict or None
        """
        super().__init__(source=source, destination=destination)
        self.punctuation = punctuation

    def __call__(self):
        d = self.load()
        fields = ['title', 'text']
        preprocessed_fields = [f'preprocessed_{x}' for x in fields]
        for f, pf in zip(fields, preprocessed_fields):
            for n in d['news']:
                source_field = pf if pf in n else f
                if self.punctuation:
                    n[pf] = n[source_field].translate(
                        str.maketrans('', '', string.punctuation))
        return self.save(d)


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
