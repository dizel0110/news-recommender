from pathlib import Path
import json
from datetime import datetime
import sys
import uuid

from gensim.models import Word2Vec
import pandas as pd
import numpy as np
import yaml


class Tester:
    def __init__(
            self,
            kind='yanr',
            raw_path='data/raw/yanr_10k.csv',
            processed_path='data/processed/yanr_10k.txt',
            map_path='data/processed/yanr_10k_map.txt',
            model_path='models/word2vec.bin.gz',
            output_path='reports/models/test.csv',
            metrics_path='reports/models/test_metrics.json',
            seed=42,
            top_n=20):
        self.kind = kind
        self.raw_path = raw_path
        self.processed_path = processed_path
        self.map_path = map_path
        self.model_path = model_path
        self.output_path = output_path
        self.metrics_path = metrics_path
        self.seed = seed
        self.top_n = top_n

    def __call__(self):
        user = input('Print your name: ')
        session = str(uuid.uuid4())
        print(f'Your session id: {session}')
        rng = np.random.default_rng(seed=self.seed)
        model = Word2Vec.load(self.model_path)
        if self.kind == 'yanr':
            df = pd.read_csv(self.raw_path)
            cols = ['title', 'summary', 'link', 'published']
        else:
            raise NotImplementedError(self.kind)
        print(f'Number of texts: {len(df)}')
        with open(self.processed_path, encoding='utf-8') as f:
            processed_data = f.readlines()
        print(f'Number of sentences: {len(processed_data)}')
        data_map = {}
        with open(self.map_path) as f:
            for line in f:
                tokens = [int(x) for x in line.split()]
                data_map.setdefault(tokens[0], []).append(tokens[1])
        print(f'Number of maps: {len(data_map)}')
        output_path = Path(self.output_path)
        report_cols = ['session', 'user', 'sample', 'datetime',
                       'a', 'rank', 'b', 'distance', 'duration', 'score']
        if not output_path.exists():
            output_path.parent.mkdir(exist_ok=True, parents=True)
            results = pd.DataFrame(columns=report_cols)
            results.to_csv(output_path)
        else:
            results = pd.read_csv(output_path)
        metrics_path = Path(self.metrics_path)
        if not metrics_path.exists():
            metrics_path.parent.mkdir(exist_ok=True, parents=True)
            metrics = {}
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f)
        else:
            with open(metrics_path) as f:
                metrics = json.load(f)
        dim = model.vector_size
        print(f'Embeddings dim: {dim}')
        embeddings = []
        sentences = []
        for i, row in df.iterrows():
            rows = data_map.get(i, [])
            ss = [processed_data[x] for x in rows]
            sentences.append(ss)
            vs = [model.wv[y] if y in model.wv else np.zeros(dim)
                  for x in ss for y in x.split()]
            if len(vs) == 0:
                embeddings.append(np.zeros(dim))
            else:
                embeddings.append(np.mean(vs, axis=0))
        embeddings = np.array(embeddings)
        print(f'Number of zero embeddings: {sum(embeddings.sum(axis=1) == 0)}')
        cnt = 0
        try:
            while True:
                start_time = datetime.utcnow()
                cnt += 1
                print(f'\nSample {cnt}')
                a = rng.integers(0, len(df))
                rank = rng.integers(1, self.top_n + 1)
                print('Are texts related?'
                      '\nPrint score from 0 (unrelated) to 1 (related) or -1 (other)'
                      '\nPrint CTRL+D to stop the session')
                dists = np.linalg.norm(embeddings - embeddings[a], axis=1)
                indexes = np.argsort(dists)
                b = indexes[rank]
                print('\nText A')
                for c in cols:
                    print(f'{c}: {df[c].iloc[a]}')
                print('\nText B')
                for c in cols:
                    print(f'{c}: {df[c].iloc[b]}')
                while True:
                    try:
                        score = input()
                        score = float(score)
                    except ValueError:
                        print('Score should be float')
                    except (EOFError, KeyboardInterrupt):
                        print('Interrupted')
                        sys.exit(0)
                    else:
                        if 0 <= score <= 1 or score == -1:
                            break
                        else:
                            print('Score should be in range [0.0, 1.0] or -1')
                trial = {x: None for x in report_cols}
                trial['session'] = session
                trial['user'] = user
                trial['sample'] = cnt
                trial['datetime'] = start_time
                trial['a'] = a
                trial['b'] = b
                trial['rank'] = rank
                trial['duration'] = datetime.utcnow() - start_time
                trial['distance'] = dists[b]
                trial['score'] = score if score >= 0 else None
                trial = pd.DataFrame([trial])
                results = pd.concat([results, trial])
                results.to_csv(output_path, index=False)
                r = results.dropna()
                metrics['mean'] = r['score'].mean()
                metrics['average_rank'] = np.average(r['score'], weights=1 / r['rank'])
                inv_distance = np.divide(1, r['distance']).astype(float)
                mask = np.isfinite(inv_distance)
                if sum(mask) > 0:
                    avg = np.average(r['score'][mask], weights=inv_distance[mask])
                else:
                    avg = None
                metrics['average_distance'] = avg
                with open(metrics_path, 'w') as f:
                    json.dump(metrics, f)
        except (EOFError, KeyboardInterrupt):
            print('Interrupted')
            sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) > 1:  # config file
        with open(sys.argv[1]) as f:
            kwargs = yaml.safe_load(f)
    else:  # default
        kwargs = {}
    Tester(**kwargs)()
