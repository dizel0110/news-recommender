from typing import Optional, Dict
from pathlib import Path

import click
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from yanr.viewer.viewer import Viewer, click_options


class Comparator(Viewer):
    def __init__(self, source: str, destination: str,
                 dist_kwargs: Optional[Dict] = None) -> None:
        """Compare two embeddings

        Args:
            source (str): url or path to file
            destination (str): url or path to file
            dist_kwargs (dict, optional): keyword arguments of scipy cdist function

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.dist_kwargs = {} if dist_kwargs is None else dist_kwargs

    def __call__(self) -> None:
        """Compare

        Returns: None
        """
        s = self.load()
        source = self.source
        self.source = s['source']
        s1 = self.load()
        self.source = s['source2']
        s2 = self.load()
        self.source = source
        fields = ['text', 'title']
        for f in fields:
            texts1 = [x[f] for x in s1['news']]
            texts2 = [x[f] for x in s2['news']]
            texts1_br = [" ".join(y if i % 5 != 0 or i == 0 else "<br>" + y
                                  for i, y in enumerate(x.split())) for x in texts1]
            texts2_br = [" ".join(y if i % 5 != 0 or i == 0 else "<br>" + y
                                  for i, y in enumerate(x.split())) for x in texts2]
            m = s[f'{f}_embedding']['vectors_vectors2']
            fig = px.imshow(m, text_auto=".2f", color_continuous_scale='Greys',
                            aspect="auto")
            cd = [[f'y_text:<br>{y}<br>x_text:<br>{x}' for x in texts2_br] for y in
                  texts1_br]
            ht = 'x: %{x}<br>y: %{y}<br>distance: %{z}<br>%{customdata}<extra></extra>'
            fig.update(data=[{'customdata': cd, 'hovertemplate': ht}])
            fig.update_layout(xaxis={'title': s['source2']},
                              yaxis={'title': s['source']})
            p = Path(self.destination) / f
            p.mkdir(parents=True, exist_ok=True)
            fig.write_html(p / 'vectors_vectors2.html')

            b = np.array(s[f'{f}_embedding']['vector_vectors2'], dtype=float)
            ind = np.argsort(b)[::-1]
            fig = go.Figure(go.Bar(
                x=[b[x] for x in ind],
                y=[texts2_br[x] for x in ind],
                orientation='h'))
            fig.update_layout(title=s['source'], yaxis={'visible': False,
                                                        'showticklabels': False})
            fig.write_html(p / 'vector_vectors2.html')

            b = np.array(s[f'{f}_embedding']['vector2_vectors'], dtype=float)
            ind = np.argsort(b)[::-1]
            fig = go.Figure(go.Bar(
                x=[b[x] for x in ind],
                y=[texts1_br[x] for x in ind],
                orientation='h'))
            fig.update_layout(title=s['source2'], yaxis={'visible': False,
                                                         'showticklabels': False})
            fig.write_html(p / 'vector2_vectors.html')


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
@click.pass_context
def comparator_cli(ctx, source, destination):
    dist_kwargs = dict(x.split('=') for x in ctx.args if '=' in x)
    Comparator(source, destination, dist_kwargs)()


if __name__ == '__main__':
    comparator_cli()
