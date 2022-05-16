from typing import Optional, Dict

import click
import numpy as np
from scipy.spatial.distance import cdist

from yanr.postprocessor.postprocessor import Postprocessor, click_options


class Comparator(Postprocessor):
    def __init__(self, source, destination, source2,
                 dist_kwargs: Optional[Dict] = None):
        """Compare two embeddings

        Args:
            source (str or dict or None): url/path, dict or None
            destination (str or dict or None): url/path, dict or None
            source2 (str): url/path, dict or None
            dist_kwargs (dict, optional): keyword arguments of scipy cdist function

        Returns: None
        """
        super().__init__(source=source, destination=destination)
        self.source2 = source2
        self.dist_kwargs = {} if dist_kwargs is None else dist_kwargs

    def __call__(self):
        d = {'source': self.source, 'source2': self.source2}
        s = self.load()
        source = self.source
        self.source = self.source2
        s2 = self.load()
        self.source = source
        self.compare(d, s, s2, 'title_embedding')
        self.compare(d, s, s2, 'text_embedding')
        return self.save(d)

    def compare(self, dst, src, src2, field):
        dst[field] = {}
        dims = {len(y) for x in src['news'] for y in x[field] if y is not None}
        dims2 = {len(y) for x in src2['news'] for y in x[field] if y is not None}
        if len(dims) != 1:
            print(f'Empty or different embedding sizes in {self.source} {field}')
            return
        if len(dims2) != 1:
            print(f'Empty or different embedding sizes in {self.source2} {field}')
            return
        dim, dim2 = list(dims)[0], list(dims2)[0],
        if dim != dim2:
            print(f'Different embedding sizes {self.source} and {self.source2} {field}')
            return
        es = [[y for y in x[field] if y is not None] for x in src['news']]
        es2 = [[y for y in x[field] if y is not None] for x in src2['news']]
        vs = [np.mean(x, axis=0) if len(x) > 0 else np.full(dim, np.inf) for x in es]
        vs2 = [np.mean(x, axis=0) if len(x) > 0 else np.full(dim, np.inf) for x in es2]
        v = np.mean([x for x in vs if not np.all(np.isinf(x))], axis=0)
        v2 = np.mean([x for x in vs2 if not np.all(np.isinf(x))], axis=0)
        vs_vs2 = cdist(vs, vs2, **self.dist_kwargs)
        v_vs2 = cdist([v], vs2, **self.dist_kwargs)[0]
        v2_vs = cdist([v2], vs, **self.dist_kwargs)[0]
        v_v2 = cdist([v], [v2], **self.dist_kwargs)[0][0]
        vs_vs2 = [[y if np.isfinite(y) else None for y in x] for x in vs_vs2.tolist()]
        v_vs2 = [x if np.isfinite(x) else None for x in v_vs2.tolist()]
        v2_vs = [x if np.isfinite(x) else None for x in v2_vs.tolist()]
        v_v2 = v_v2 if np.isfinite(v_v2) else None
        v = [x if np.isfinite(x) else None for x in v.tolist()]
        v2 = [x if np.isfinite(x) else None for x in v2.tolist()]
        vs = [[y if np.isfinite(y) else None for y in x] for x in vs]
        vs2 = [[y if np.isfinite(y) else None for y in x] for x in vs2]
        dst[field]['vector'] = v
        dst[field]['vector2'] = v2
        dst[field]['vectors'] = vs
        dst[field]['vectors2'] = vs2
        dst[field]['vectors_vectors2'] = vs_vs2
        dst[field]['vector_vectors2'] = v_vs2
        dst[field]['vector2_vectors'] = v2_vs
        dst[field]['vector_vector2'] = v_v2


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
@click.option('-s2', '--source2', help='url or path to file to compare with source')
@click.pass_context
def comparator_cli(ctx, source, destination, source2):
    dist_kwargs = dict(x.split('=') for x in ctx.args if '=' in x)
    Comparator(source, destination, source2, dist_kwargs)()


if __name__ == '__main__':
    comparator_cli()
