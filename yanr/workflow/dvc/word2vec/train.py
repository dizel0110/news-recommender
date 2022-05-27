from pathlib import Path
import json
import time

import click
import gensim.models


@click.command()
@click.option('--input-path', '-i', help='Path to dataset')
@click.option('--output-path', '-o', help='Path to output file')
@click.option('--metrics_path', '-m', help='Path to metrics file')
@click.option('--vector-size', default=100, help='')
@click.option('--alpha', default=0.025, help='')
@click.option('--window', default=5, help='')
@click.option('--min-count', default=5, help='')
@click.option('--max-vocab-size', default=None, type=int, help='')
@click.option('--sample', default=0.001, help='')
@click.option('--seed', default=42, help='')
@click.option('--workers', default=1, help='')
@click.option('--min-alpha', default=0.0001, help='')
@click.option('--sg', default=0, help='')
@click.option('--hs', default=0, help='')
@click.option('--negative', default=5, help='')
@click.option('--ns-exponent', default=0.75, help='')
@click.option('--cbow-mean', default=1, help='')
@click.option('--epochs', default=5, help='')
@click.option('--batch-words', default=10000, help='')
@click.option('--max-final-vocab', default=None, type=int, help='')
@click.option('--shrink-windows', default=1, help='')
def main(input_path, output_path, metrics_path,
         vector_size, alpha, window, min_count, max_vocab_size, sample, seed, workers,
         min_alpha, sg, hs, negative, ns_exponent, cbow_mean,
         epochs, batch_words, max_final_vocab, shrink_windows):
    start_time = time.perf_counter()
    model = gensim.models.Word2Vec(
        corpus_file=input_path,
        vector_size=vector_size,
        alpha=alpha,
        window=window,
        min_count=min_count,
        max_vocab_size=max_vocab_size,
        sample=sample,
        seed=seed,
        workers=workers,
        min_alpha=min_alpha,
        sg=sg,
        hs=hs,
        negative=negative,
        ns_exponent=ns_exponent,
        cbow_mean=cbow_mean,
        epochs=epochs,
        batch_words=batch_words,
        compute_loss=True,
        max_final_vocab=max_final_vocab,
        shrink_windows=shrink_windows)
    delta_time = time.perf_counter() - start_time
    training_loss = model.get_latest_training_loss()
    vocabulary_size = len(model.wv)
    metrics_path = Path(metrics_path)
    metrics_path.parent.mkdir(exist_ok=True, parents=True)
    with open(metrics_path, 'w') as f:
        json.dump({'train': {'loss': training_loss,
                             'vocabulary_size': vocabulary_size,
                             'time': delta_time}}, f)
    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    model.save(str(output_path))


if __name__ == '__main__':
    main()
