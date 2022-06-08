"""Optuna Optimizer

https://optuna.readthedocs.io/en/stable/reference/samplers.html
https://optuna.readthedocs.io/en/stable/reference/pruners.html


"""
import json
import os
import subprocess
import copy
import io
from pathlib import Path
import yaml
import sys

import optuna
from dotenv import load_dotenv


class Optimizer:
    def __init__(self, n_trials=None, timeout=None, load_if_exists=False,
                 sampler=None, sampler_kwargs=None,
                 pruner=None, pruner_kwargs=None,
                 subprocess_kwargs=None, stdout_kwargs=None, stderr_kwargs=None,
                 params=None, metrics=None):
        self.n_trials = n_trials
        self.timeout = timeout
        self.load_if_exists = load_if_exists
        self.sampler = sampler
        self.sampler_kwargs = sampler_kwargs
        self.pruner = pruner
        self.pruner_kwargs = pruner_kwargs
        self.subprocess_kwargs = {} if subprocess_kwargs is None else subprocess_kwargs
        self.stdout_kwargs = {} if stdout_kwargs is None else stdout_kwargs
        self.stderr_kwargs = {} if stderr_kwargs is None else stderr_kwargs
        self.params = {} if params is None else params
        self.metrics = {} if metrics is None else metrics

    def subprocess(self):
        subprocess_kwargs = copy.deepcopy(self.subprocess_kwargs)
        stdout = self.subprocess_kwargs.get('stdout', None)
        if stdout is not None:
            if stdout in ['PIPE', 'STDOUT', 'DEVNULL']:
                stdout = getattr(subprocess, stdout)
            else:  # FILE
                stdout = open(file=stdout, **self.stdout_kwargs)
            subprocess_kwargs['stdout'] = stdout
        stderr = subprocess_kwargs.get('stderr', None)
        if stderr is not None:
            if stderr in ['PIPE', 'STDOUT', 'DEVNULL']:
                stderr = getattr(subprocess, stderr)
            else:  # FILE
                stderr = open(file=stderr, **self.stderr_kwargs)
            subprocess_kwargs['stderr'] = stderr
        result = subprocess.run(**subprocess_kwargs)
        if isinstance(stdout, io.IOBase) and not stdout.closed:
            stdout.close()
        if isinstance(stderr, io.IOBase) and not stderr.closed:
            stderr.close()
        return result

    @staticmethod
    def initialize_sampler(sampler, sampler_kwargs):
        if sampler is None:
            return sampler
        elif sampler != 'PartialFixedSampler':
            return getattr(optuna.samplers, sampler)(**sampler_kwargs)
        else:
            ss_kwargs = copy.deepcopy(sampler_kwargs)
            ss = Optimizer.initialize_sampler(
                ss_kwargs['base_sampler'],
                ss_kwargs['base_sampler_kwargs'])
            ss_kwargs['base_sampler'] = ss
            ss_kwargs.pop('base_sampler_kwargs')
            return Optimizer.initialize_sampler(sampler, ss_kwargs)

    @staticmethod
    def initialize_pruner(pruner, pruner_kwargs):
        if pruner is None:
            return pruner
        elif pruner != 'PatientPruner':
            return getattr(optuna.pruners, pruner)(**pruner_kwargs)
        else:
            pp_kwargs = copy.deepcopy(pruner_kwargs)
            pp = Optimizer.initialize_pruner(
                pp_kwargs['wrapped_pruner'],
                pp_kwargs['wrapped_pruner_kwargs'])
            pp_kwargs['wrapped_pruner'] = pp
            pp_kwargs.pop('wrapped_pruner_kwargs')
            return Optimizer.initialize_pruner(pruner, pp_kwargs)

    def set_params(self, trial):
        for path, kwargs in self.params.items():
            local_path, global_path = path.split('@')
            method = getattr(trial, kwargs['method'])
            m = kwargs.pop('method')
            kwargs.setdefault('name', local_path)
            v = method(**kwargs)
            kwargs['method'] = m
            gp = Path(global_path)
            with open(gp) as f:
                if gp.suffix == '.json':
                    data = json.load(f)
                elif gp.suffix == '.yaml':
                    data = yaml.safe_load(f)
                else:
                    raise NotImplementedError(gp)
            d = data
            for p in local_path.split('.'):
                if isinstance(d, (list, dict)):
                    p = int(p) if isinstance(d, list) else p
                    if isinstance(d[p], (list, dict)):
                        d = d[p]
                    else:
                        d[p] = v
            with open(gp, 'w') as f:
                if gp.suffix == '.json':
                    json.dump(data, f)
                elif gp.suffix == '.yaml':
                    yaml.safe_dump(data, f)
                else:
                    raise NotImplementedError(gp)

    def get_metrics(self, trial):
        values = []
        for path, direction in self.metrics.items():
            local_path, global_path = path.split('@')
            gp = Path(global_path)
            with open(gp) as f:
                if gp.suffix == '.json':
                    data = json.load(f)
                elif gp.suffix == '.yaml':
                    data = yaml.safe_load(f)
                else:
                    raise NotImplementedError(gp)
            d = data
            for p in local_path.split('.'):
                if isinstance(d, (list, dict)):
                    p = int(p) if isinstance(d, list) else p
                    if isinstance(d[p], (list, dict)):
                        d = d[p]
                    else:
                        v = d[p]
                        values.append(v)
        return tuple(values)

    def objective(self, trial):
        self.set_params(trial)
        r = self.subprocess()
        print(r)
        return self.get_metrics(trial)

    def __call__(self):
        load_dotenv()
        s = self.initialize_sampler(self.sampler, self.sampler_kwargs)
        p = self.initialize_pruner(self.pruner, self.pruner_kwargs)
        directions = list(self.metrics.values())
        if len(directions) == 1:
            study = optuna.create_study(storage=os.getenv('OPTUNA_URL'),
                                        study_name=os.getenv('OPTUNA_STUDY'),
                                        load_if_exists=self.load_if_exists,
                                        sampler=s, pruner=p,
                                        direction=directions[0])
        else:  # multi-objective
            study = optuna.create_study(storage=os.getenv('OPTUNA_URL'),
                                        study_name=os.getenv('OPTUNA_STUDY'),
                                        load_if_exists=self.load_if_exists,
                                        sampler=s, pruner=p,
                                        directions=directions)
        study.optimize(self.objective, n_trials=self.n_trials, timeout=self.timeout)


if __name__ == '__main__':
    if len(sys.argv) > 1:  # config file
        with open(sys.argv[1]) as f:
            kwargs = yaml.safe_load(f)
    else:  # default
        kwargs = {}
    Optimizer(**kwargs)()
