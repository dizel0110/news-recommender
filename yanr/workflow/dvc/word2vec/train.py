from pathlib import Path
import json
import time
from pprint import pprint
import sys
from dataclasses import dataclass

import yaml
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
import pandas as pd


@dataclass
class Trainer:
    def __init__(
            self,
            processed_path='data/processed/yanr_10k.txt',
            output_path='models/word2vec.bin.gz',
            metrics_path='reports/models/train_metrics.json',
            plots_path='reports/models/train_plots.csv',
            model_path=None, vector_size=100, alpha=0.025, window=5, min_count=5,
            max_vocab_size=None, sample=1e-3, seed=1, workers=1, min_alpha=0.0001, sg=0,
            hs=0, negative=5, ns_exponent=0.75, cbow_mean=1, epochs=5,
            batch_words=10000, max_final_vocab=None, shrink_windows=True):
        self.processed_path = processed_path
        self.output_path = output_path
        self.metrics_path = metrics_path
        self.plots_path = plots_path
        self.model_path = model_path
        self.vector_size = vector_size
        self.alpha = alpha
        self.window = window
        self.min_count = min_count
        self.max_vocab_size = max_vocab_size
        self.sample = sample
        self.seed = seed
        self.workers = workers
        self.min_alpha = min_alpha
        self.sg = sg
        self.hs = hs
        self.negative = negative
        self.ns_exponent = ns_exponent
        self.cbow_mean = cbow_mean
        self.epochs = epochs
        self.batch_words = batch_words
        self.max_final_vocab = max_final_vocab
        self.shrink_windows = shrink_windows

    def __call__(self):
        logger = Logger(self.output_path, self.metrics_path, self.plots_path)
        if self.model_path is None:  # Train
            Word2Vec(
                corpus_file=self.processed_path,
                vector_size=self.vector_size,
                alpha=self.alpha,
                window=self.window,
                min_count=self.min_count,
                max_vocab_size=self.max_vocab_size,
                sample=self.sample,
                seed=self.seed,
                workers=self.workers,
                min_alpha=self.min_alpha,
                sg=self.sg,
                hs=self.hs,
                negative=self.negative,
                ns_exponent=self.ns_exponent,
                cbow_mean=self.cbow_mean,
                epochs=self.epochs,
                batch_words=self.batch_words,
                compute_loss=True,
                callbacks=[logger],
                max_final_vocab=self.max_final_vocab,
                shrink_windows=self.shrink_windows)
        else:  # Fine-tune
            model_path = Path(self.model_path)
            model = Word2Vec.load(str(model_path))
            model.build_vocab(corpus_file=self.processed_path, update=True)
            model.train(corpus_file=self.processed_path,
                        total_examples=model.corpus_count,
                        total_words=model.corpus_total_words,
                        epochs=self.epochs,
                        compute_loss=True,
                        callbacks=[logger])


class Logger(CallbackAny2Vec):
    """Word2Vec logger

    See Also:
        https://stackoverflow.com/questions/52038651/loss-does-not-decrease-during-training-word2vec-gensim

    """

    def __init__(self, output_path, metrics_path, plots_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        metrics_path = Path(metrics_path)
        metrics_path.parent.mkdir(exist_ok=True, parents=True)
        self.metrics_path = metrics_path
        self.output_path = output_path
        plots_path = Path(plots_path)
        plots_path.parent.mkdir(exist_ok=True, parents=True)
        self.plots_path = plots_path
        self.df = pd.DataFrame(columns=['epoch', 'train_time', 'train_loss'])
        self.start_time = None
        self.epoch_start_time = None

    def on_train_begin(self, model):
        print("Training starts")
        self.start_time = time.perf_counter()

    def on_epoch_begin(self, model):
        self.epoch_start_time = time.perf_counter()

    def on_epoch_end(self, model):
        epoch_time = time.perf_counter() - self.epoch_start_time
        prev_loss = self.df['train_loss'].iloc[-1] if len(self.df) > 0 else 0
        loss = model.get_latest_training_loss() - prev_loss
        n = model.epochs
        print(f"Epoch: {len(self.df) + 1}/{n}, loss: {loss}, time: {epoch_time:0.3f}s")
        last_df = pd.DataFrame({'epoch': [len(self.df)], 'train_time': epoch_time,
                                'train_loss': [loss]})
        self.df = pd.concat([self.df, last_df])
        self.df.to_csv(self.plots_path, index=False)

    def on_train_end(self, model):
        train_time = time.perf_counter() - self.start_time
        print("Training ends")
        loss = self.df['train_loss'].iloc[-1]
        vocabulary_size = len(model.wv)
        metrics = {'time': train_time,
                   'loss': loss,
                   'vocabulary': vocabulary_size}
        pprint(metrics)
        with open(self.metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        model.save(str(self.output_path))


if __name__ == '__main__':
    if len(sys.argv) > 1:  # config file
        with open(sys.argv[1]) as f:
            kwargs = yaml.safe_load(f)
    else:  # default
        kwargs = {}
    Trainer(**kwargs)()
