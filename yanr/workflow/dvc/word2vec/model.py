"""Gensim Word2Vec as MLflow Model

References:
    https://www.mlflow.org/docs/latest/model-registry.html#registering-an-unsupported-machine-learning-model
"""
import os
from pathlib import Path
import json

import numpy as np
from mlflow.pyfunc import PythonModel
import yaml
import boto3
from gensim.models import Word2Vec

from preprocess import Preprocessor


class Recommender(PythonModel):
    """
    Class to train and use FastText Models
    """

    def __init__(self):
        self.preprocessor = None
        self.model = None
        self.news = []
        self.vectors = []

    def get_news(self, kind='memory', n=20, output=None):
        s3 = boto3.resource(
            service_name='s3',
            region_name='ru-central1',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=os.environ.get('YANR_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('YANR_SECRET_ACCESS_KEY'))
        bucket = s3.Bucket('yanr')
        objects = bucket.objects.filter(Prefix="news/")
        if kind == 'count':
            return sum(1 for _ in objects)
        elif kind == 'files':
            n = min(sum(1 for _ in objects), n) if n is not None else sum(
                1 for _ in objects)
            output = Path(output)
            output.mkdir(exist_ok=True, parents=True)
            for i, o in enumerate(
                    sorted(objects, key=lambda x: x.last_modified, reverse=True)[:n]):
                p = output / o.key[5:]
                print(f'{i + 1}/{n} {o.last_modified} {o.key} -> {p}')
                bucket.download_file(o.key, str(p))
        elif kind == 'memory':
            n = min(sum(1 for _ in objects), n) if n is not None else sum(
                1 for _ in objects)
            news = []
            for i, o in enumerate(
                    sorted(objects, key=lambda x: x.last_modified, reverse=True)[:n]):
                d = json.loads(o.get()['Body'].read().decode())
                print(f'{i + 1}/{n} {o.last_modified} {d.get("title", "")}')
                news.append(d)
            return news
        else:
            raise ValueError(kind)

    def load_context(self, context):
        """This method is called when loading an MLflow model with pyfunc.load_model(),
         as soon as the Python Model is constructed.
        Args:
            context: MLflow context where the model artifact is stored.
        """
        with open(context.artifacts["preprocessor_params"]) as f:
            params = yaml.safe_load(f)
            params['kind'] = 'list'
            params['raw_path'] = None
            params['processed_path'] = None
            params['map_path'] = None
            params['report_path'] = None
            params['words_path'] = None
            params['words_lengths_path'] = None
            params['sentences_lengths_path'] = None
            params['min_word_length'] = 1
            params['min_sentence_length'] = 1
        self.preprocessor = Preprocessor(**params)
        self.model = Word2Vec.load(context.artifacts["model_path"])
        # self.news = self.get_news(n=100)
        # self.vectors = self.vectorize([[x.get('title', ''), x.get('summary', '')]
        #                                for x in self.news])

    def vectorize(self, texts):
        # [[text, text, ...], [text, ], ...]
        dim = self.model.vector_size
        self.preprocessor.raw_path = texts
        ss = self.preprocessor()  # sentences
        vectors = []
        for i, d in enumerate(ss):
            # For text in document for sentence in text for word in sentence
            vs = [self.model.wv[z] if z in self.model.wv else np.zeros(dim)
                  for x in d for y in x for z in y]
            if len(vs) == 0:
                vectors.append(np.zeros(dim))
            else:
                vectors.append(np.mean(vs, axis=0))
        vectors = np.array(vectors)
        return vectors

    def predict(self, context, model_input):
        """This is an abstract function.
        Args:
            context ([type]): MLflow context where the model artifact is stored.
            model_input ([type]): the input data to fit into the model.
        Returns:
            [type]: the loaded model artifact.
        """
        text = model_input['text']
        n = model_input['n']
        top = model_input['top']
        self.news = self.get_news(n=n)
        self.vectors = self.vectorize([[x.get('title', ''), x.get('summary', '')]
                                       for x in self.news])
        v = self.vectorize([[text]])[0]
        dists = np.linalg.norm(self.vectors - v, axis=1)
        indexes = np.argsort(dists)[:top]
        return [self.news[i] for i in indexes]


if __name__ == '__main__':
    pass
    # # Set the tracking URI to use local SQLAlchemy db file and start the run
    # # Log MLflow entities and save the model
    # # mlflow.set_tracking_uri("sqlite:///mlflow.db")
    # # Save the conda environment for this model.
    # load_dotenv()
    #
    # artifacts = {
    #     "model_path": "models/word2vec.bin.gz",
    #     "preprocessor_params": 'params_preprocess.yaml'
    # }
    # model_path = "models/word2vec"
    # reg_model_name = "recommender"
    # m = Recommender()
    # # Use the saved model path to log and register into the model registry
    # log_model(artifact_path=model_path,
    #           python_model=m,
    #           registered_model_name=reg_model_name,
    #           artifacts=artifacts)
    # # --backend-store-uri sqlite:///mlflow.db
    # # –-env-manager=local or --no-conda
    # # Load the model from the model registry and predict
    # model_uri = f"models:/{reg_model_name}/latest"
    # m = load_model(model_uri=model_uri)
    # print(m.predict({'text': 'BTC ETC', "n": 10}))
