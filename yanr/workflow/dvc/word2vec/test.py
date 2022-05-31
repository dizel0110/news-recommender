from pathlib import Path
import json
from datetime import datetime
import sys
import uuid
from pprint import pprint

from gensim.models import Word2Vec
import pandas as pd
import numpy as np
import yaml

from preprocess import Preprocessor


class Tester:
    def __init__(
            self,
            kind='yanr',
            raw_path='data/raw/yanr_10k.csv',
            preprocessor_params='params_preprocess.yaml',
            model_path='models/word2vec.bin.gz',
            output_path='reports/models/test.csv',
            metrics_path='reports/models/test_metrics.json',
            seed=42,
            top_n=20):
        self.kind = kind
        self.raw_path = raw_path
        self.preprocessor_params = preprocessor_params
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
            data_cols = ['title', 'summary']
            docs = [[x[y] for y in data_cols] for _, x in df.iterrows()]
            meta_cols = ['link', 'published']
            meta = [{y: x[y] for y in meta_cols} for _, x in df.iterrows()]
        elif self.kind == 'list':
            docs = self.raw_path
            meta = [{} for _ in docs]
        else:
            raise NotImplementedError(self.kind)
        print(f'Number of texts: {len(docs)}')
        output_path = Path(self.output_path)
        report_cols = ['session', 'user', 'sample', 'datetime', 'text',
                       'a', 'b', 'rank', 'distance', 'duration', 'score']
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
        with open(self.preprocessor_params) as f:
            params = yaml.safe_load(f)
            params['kind'] = 'list'
            params['raw_path'] = docs
            params['processed_path'] = None
            params['map_path'] = None
            params['report_path'] = None
            params['words_path'] = None
            params['words_lengths_path'] = None
            params['sentences_lengths_path'] = None
        pp = Preprocessor(**params)
        ss = pp()  # convert documents to sentences
        for i, d in enumerate(ss):
            # For text in document for sentence in text for word in sentence
            vs = [model.wv[z] if z in model.wv else np.zeros(dim)
                  for x in d for y in x for z in y]
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
                kind = rng.integers(0, 2)
                if kind == 0:  # Text to text
                    print('Are texts related?'
                          '\nPrint score from 0 (unrelated) to 1 (related) '
                          'or -1 (other)'
                          '\nPrint CTRL+D to stop the session')
                    text = None
                    a = rng.integers(0, len(docs))
                    rank = rng.integers(1, self.top_n + 1)
                    dists = np.linalg.norm(embeddings - embeddings[a], axis=1)
                    indexes = np.argsort(dists)
                    b = indexes[rank]
                    print('\nText A')
                    pprint(docs[a])
                    pprint(meta[a])
                    print('\nText B')
                    pprint(docs[b])
                    pprint(meta[b])
                else:  # User to text
                    while True:
                        try:
                            text = input('Input some text to find related text: ')
                            text_ds = [[text]]
                            pp.raw_path = text_ds
                            text_ss = pp()
                            vs = [model.wv[z] if z in model.wv else np.zeros(dim)
                                  for x in text_ss[0] for y in x for z in y]
                            if len(vs) == 0:
                                emb = np.zeros(dim)
                            else:
                                emb = np.mean(vs, axis=0)
                        except (EOFError, KeyboardInterrupt):
                            print('Interrupted')
                            sys.exit(0)
                        except Exception:
                            print('Something went wrong... Try another (longer) text!')
                        else:
                            break
                    print('Is this text related to your text?'
                          '\nPrint score from 0 (unrelated) to 1 (related) '
                          'or -1 (other)'
                          '\nPrint CTRL+D to stop the session')
                    rank = rng.integers(1, self.top_n + 1)
                    dists = np.linalg.norm(embeddings - emb, axis=1)
                    indexes = np.argsort(dists)
                    a = None
                    b = indexes[rank]
                    print('\nText A')
                    pprint(text_ds[0])
                    pprint({'processed_text': text_ss[0]})
                    print('\nText B')
                    pprint(docs[b])
                    pprint(meta[b])
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
                trial['text'] = text
                trial['a'] = a
                trial['b'] = b
                trial['rank'] = rank
                trial['duration'] = datetime.utcnow() - start_time
                trial['distance'] = dists[b]
                trial['score'] = score if score >= 0 else None
                trial = pd.DataFrame([trial])
                results = pd.concat([results, trial])
                results.to_csv(output_path, index=False)
                r = results.dropna(subset=['score'])
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
