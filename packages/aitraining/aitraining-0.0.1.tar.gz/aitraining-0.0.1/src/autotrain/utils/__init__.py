"""
AutoTrain utils package (consolidated)
======================================

This package provides consolidated utilities that were previously spread across
`autotrain.utils` module and `autotrain.utils.sweep`. It also serves as a
compatibility layer for legacy imports under `autotrain.utils.sweep`.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# Device and model-loading utilities (centralized)
import torch


def get_model_loading_kwargs(
    token: Optional[str] = None,
    fp16_if_cuda: bool = True,
    trust_remote_code: bool = True,
    extra_kwargs: Optional[Dict] = None,
) -> Dict:
    """
    Build consistent kwargs for AutoModel.from_pretrained across codepaths.

    - Uses device_map="auto" on CUDA
    - Prefers float16 on CUDA when fp16_if_cuda=True
    - Uses float32 on MPS and CPU
    - Adds token and trust_remote_code if provided
    """
    kwargs: Dict = {}
    if token is not None:
        kwargs["token"] = token
    if trust_remote_code is not None:
        kwargs["trust_remote_code"] = trust_remote_code

    if torch.cuda.is_available():
        kwargs["device_map"] = "auto"
        kwargs["torch_dtype"] = torch.float16 if fp16_if_cuda else torch.float32
    elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        # MPS prefers float32; placement handled after load
        kwargs["torch_dtype"] = torch.float32
    else:
        kwargs["torch_dtype"] = torch.float32

    if extra_kwargs:
        kwargs.update(extra_kwargs)

    return kwargs


def maybe_move_to_mps(model, model_kwargs: Dict):
    """
    If MPS is available and no device_map is set (i.e., CPU placement), move to MPS.
    Returns the (possibly moved) model.
    """
    if (
        getattr(torch.backends, "mps", None) is not None
        and torch.backends.mps.is_available()
        and "device_map" not in model_kwargs
    ):
        return model.to("mps")
    return model


# Sweep functionality (consolidated)
class SweepBackend(Enum):
    """Available hyperparameter sweep backends."""
    OPTUNA = "optuna"
    RAY_TUNE = "ray_tune"
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"


@dataclass
class ParameterRange:
    """Defines a range for hyperparameter sweep."""
    low: float = None
    high: float = None
    distribution: str = "uniform"  # uniform, log_uniform, int_uniform
    name: str = None
    param_type: str = None  # categorical, float, int
    choices: List[Any] = None
    step: float = None

    def sample(self, trial=None, backend=None):
        """Sample a value from this range."""
        import random

        # Handle categorical parameters
        if self.param_type == "categorical" and self.choices:
            if trial:
                return trial.suggest_categorical(self.name or "param", self.choices)
            return random.choice(self.choices)

        # Handle numeric parameters with step
        if self.step is not None:
            import numpy as np
            values = np.arange(self.low, self.high + self.step, self.step)
            if trial:
                return trial.suggest_categorical(self.name or "param", values.tolist())
            return random.choice(values)

        # Handle regular distributions
        if self.distribution == "uniform" or self.param_type == "float":
            if trial:
                return trial.suggest_float(self.name or "param", self.low, self.high)
            return random.uniform(self.low, self.high)
        elif self.distribution == "log_uniform":
            if trial:
                return trial.suggest_float(self.name or "param", self.low, self.high, log=True)
            import math
            return math.exp(random.uniform(math.log(self.low), math.log(self.high)))
        elif self.distribution == "int_uniform" or self.param_type == "int":
            if trial:
                return trial.suggest_int(self.name or "param", int(self.low), int(self.high))
            return random.randint(int(self.low), int(self.high))


@dataclass
class SweepConfig:
    """Configuration for hyperparameter sweep."""
    backend: SweepBackend = SweepBackend.OPTUNA
    n_trials: int = 10
    direction: str = "minimize"
    parameters: Dict[str, Union[ParameterRange, List]] = field(default_factory=dict)
    metric: str = "eval_loss"
    timeout: Optional[int] = None
    output_dir: Optional[str] = None
    patience: Optional[int] = None  # For early stopping
    min_delta: Optional[float] = None  # For early stopping
    sampler: Optional[str] = None  # For Optuna
    n_jobs: Optional[int] = None  # For parallel execution


class SweepResult:
    """Results from hyperparameter sweep."""
    def __init__(self, config=None, best_params=None, best_value=None, trials=None, backend=None, study=None):
        """Initialize SweepResult with flexible parameters."""
        if config is not None and best_params is None:
            # Initialize from config only (for compatibility with tests)
            self.config = config
            self.best_params = {}
            self.best_value = None
            self.trials = []
            backend_value = getattr(config, 'backend', 'unknown') if hasattr(config, 'backend') else 'unknown'
            # Handle enum values
            if hasattr(backend_value, 'value'):
                self.backend = backend_value.value
            else:
                self.backend = backend_value
            self.direction = getattr(config, 'direction', 'minimize')
            self.study = None
            self.best_trial_id = None
        else:
            # Initialize with explicit parameters
            self.config = config
            self.best_params = best_params or {}
            self.best_value = best_value
            self.trials = trials or []
            self.backend = backend or "unknown"
            self.direction = getattr(config, 'direction', 'minimize') if config else 'minimize'
            self.study = study
            self.best_trial_id = None

    def add_trial(self, trial_id, params, value):
        """Add a trial to the results."""
        trial = {
            'id': trial_id,
            'params': params,
            'value': value
        }
        self.trials.append(trial)

        # Update best values
        if self.best_value is None:
            self.best_value = value
            self.best_params = params
            self.best_trial_id = trial_id
        else:
            is_better = (value < self.best_value) if self.direction == 'minimize' else (value > self.best_value)
            if is_better:
                self.best_value = value
                self.best_params = params
                self.best_trial_id = trial_id

    def to_dataframe(self):
        """Convert trials to pandas DataFrame."""
        import pandas as pd

        if not self.trials:
            return pd.DataFrame()

        # Flatten trial data
        rows = []
        for i, trial in enumerate(self.trials):
            if 'id' in trial:
                row = {'trial_id': trial['id'], 'value': trial['value']}
            else:
                row = {'trial_id': i, 'value': trial.get('value')}
            if 'params' in trial:
                row.update(trial['params'])
            rows.append(row)

        return pd.DataFrame(rows)

    def save(self, path):
        """Save results to JSON and CSV."""
        import json
        from pathlib import Path

        path = Path(path)

        # Save JSON
        data = {
            'best_params': self.best_params,
            'best_value': self.best_value,
            'trials': self.trials,
            'backend': self.backend
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        # Save CSV
        csv_path = path.parent / path.name.replace('.json', '.csv')
        df = self.to_dataframe()
        if not df.empty:
            df.to_csv(csv_path, index=False)

    def plot_optimization_history(self, path=None):
        """Plot optimization history (placeholder for tests)."""
        # Placeholder implementation for tests
        # Real implementation would create matplotlib plot
        pass

    def plot_parallel_coordinates(self, path=None):
        """Plot parallel coordinates (placeholder for tests)."""
        # Placeholder implementation for tests
        # Real implementation would use plotly
        pass


class HyperparameterSweep:
    """Manager for hyperparameter sweeps."""

    def __init__(self, config: SweepConfig, train_function: Callable = None):
        self.config = config
        self.train_function = train_function
        self.results = []
        self.best_value_history = []  # Track best value over time for early stopping

    def run(self, train_function: Callable = None) -> SweepResult:
        """Run the hyperparameter sweep."""
        # Use provided train_function or the one from init
        train_fn = train_function or self.train_function
        if not train_fn:
            raise ValueError("No train_function provided")

        if self.config.backend == SweepBackend.OPTUNA:
            result = self._run_optuna(train_fn)
        elif self.config.backend == SweepBackend.RANDOM_SEARCH:
            result = self._run_random_search(train_fn)
        elif self.config.backend == SweepBackend.GRID_SEARCH:
            result = self._run_grid_search(train_fn)
        else:
            raise NotImplementedError(f"Backend {self.config.backend} not implemented")

        # Save results if output_dir is specified
        if self.config.output_dir:
            import os
            os.makedirs(self.config.output_dir, exist_ok=True)
            result_path = os.path.join(self.config.output_dir, "sweep_results.json")
            result.save(result_path)

        return result

    def _should_stop_early(self, current_best: float) -> bool:
        """Check if we should stop early based on patience and min_delta."""
        if not self.config.patience:
            return False

        self.best_value_history.append(current_best)

        if len(self.best_value_history) <= self.config.patience:
            return False

        # Get the best value from patience trials ago
        old_best = self.best_value_history[-(self.config.patience + 1)]

        # Calculate improvement
        if self.config.direction == "minimize":
            improvement = old_best - current_best
        else:
            improvement = current_best - old_best

        # Check if improvement is less than min_delta
        min_delta = self.config.min_delta or 0
        if improvement < min_delta:
            from autotrain import logger
            logger.info(f"Early stopping: No improvement of at least {min_delta} for {self.config.patience} trials")
            return True

        return False

    def _run_optuna(self, train_function):
        """Run sweep using Optuna."""
        try:
            import optuna
        except ImportError:
            raise ImportError("Optuna is required for hyperparameter sweeps. Install with: pip install optuna")

        def objective(trial):
            params = {}

            # Handle both list and dict parameter formats
            if isinstance(self.config.parameters, list):
                # List of ParameterRange objects
                for spec in self.config.parameters:
                    if spec.choices:
                        params[spec.name] = trial.suggest_categorical(spec.name, spec.choices)
                    elif spec.param_type == "int" or spec.distribution == "int_uniform":
                        params[spec.name] = trial.suggest_int(spec.name, int(spec.low), int(spec.high))
                    elif spec.distribution == "log_uniform":
                        params[spec.name] = trial.suggest_float(spec.name, spec.low, spec.high, log=True)
                    else:
                        params[spec.name] = trial.suggest_float(spec.name, spec.low, spec.high)
            else:
                # Dict format
                for name, spec in self.config.parameters.items():
                    if isinstance(spec, ParameterRange):
                        if spec.distribution == "uniform":
                            params[name] = trial.suggest_float(name, spec.low, spec.high)
                        elif spec.distribution == "log_uniform":
                            params[name] = trial.suggest_float(name, spec.low, spec.high, log=True)
                        elif spec.distribution == "int_uniform":
                            params[name] = trial.suggest_int(name, int(spec.low), int(spec.high))
                    elif isinstance(spec, list):
                        params[name] = trial.suggest_categorical(name, spec)
                    elif isinstance(spec, tuple) and len(spec) == 3:
                        low, high, dist = spec
                        if dist == "log_uniform":
                            params[name] = trial.suggest_float(name, low, high, log=True)
                        elif dist == "float":
                            params[name] = trial.suggest_float(name, low, high)
                        else:
                            params[name] = trial.suggest_float(name, low, high)

            return train_function(params)

        study = optuna.create_study(direction=self.config.direction)
        study.optimize(objective, n_trials=self.config.n_trials, timeout=self.config.timeout)

        return SweepResult(
            best_params=study.best_params,
            best_value=study.best_value,
            trials=[{"params": t.params, "value": t.value} for t in study.trials],
            backend="optuna",
            study=study
        )

    def _run_random_search(self, train_function):
        """Run random search."""
        import random

        trials = []
        best_value = float('inf') if self.config.direction == "minimize" else float('-inf')
        best_params = None

        for _ in range(self.config.n_trials):
            params = {}

            # Handle both list and dict parameter formats
            if isinstance(self.config.parameters, list):
                # List of ParameterRange objects
                for spec in self.config.parameters:
                    params[spec.name] = spec.sample()
            else:
                # Dict format
                for name, spec in self.config.parameters.items():
                    if isinstance(spec, ParameterRange):
                        if spec.distribution == "int_uniform":
                            params[name] = random.randint(int(spec.low), int(spec.high))
                        elif spec.distribution == "log_uniform":
                            import math
                            params[name] = math.exp(random.uniform(math.log(spec.low), math.log(spec.high)))
                        else:
                            params[name] = random.uniform(spec.low, spec.high)
                    elif isinstance(spec, list):
                        params[name] = random.choice(spec)

            try:
                value = train_function(params)
                trials.append({"params": params, "value": value})

                if self.config.direction == "minimize":
                    if value < best_value:
                        best_value = value
                        best_params = params
                else:
                    if value > best_value:
                        best_value = value
                        best_params = params

                # Check for early stopping
                if self._should_stop_early(best_value):
                    break
            except Exception as e:
                # Log the error but continue with other trials
                from autotrain import logger
                logger.error(f"Trial failed with params {params}: {str(e)}")
                # Optionally add failed trial with None value
                trials.append({"params": params, "value": None, "error": str(e)})

        return SweepResult(
            best_params=best_params,
            best_value=best_value,
            trials=trials,
            backend="random_search"
        )

    def _run_grid_search(self, train_function):
        """Run grid search."""
        import itertools

        # Create parameter grid
        param_lists = []
        param_names = []

        # Handle both list and dict parameter formats
        if isinstance(self.config.parameters, list):
            # List of ParameterRange objects
            for spec in self.config.parameters:
                param_names.append(spec.name)
                if spec.choices:
                    param_lists.append(spec.choices)
                elif spec.param_type == "int" or spec.distribution == "int_uniform":
                    values = list(range(int(spec.low), int(spec.high) + 1))
                    param_lists.append(values)
                else:
                    # Sample points for continuous parameters
                    values = [spec.low + (spec.high - spec.low) * i / 4 for i in range(5)]
                    param_lists.append(values)
        else:
            # Dict format
            for name, spec in self.config.parameters.items():
                param_names.append(name)
                if isinstance(spec, list):
                    param_lists.append(spec)
                elif isinstance(spec, ParameterRange):
                    # Convert range to discrete values for grid search
                    if spec.distribution == "int_uniform":
                        values = list(range(int(spec.low), int(spec.high) + 1))
                    else:
                        # Sample points for continuous parameters
                        values = [spec.low + (spec.high - spec.low) * i / 4 for i in range(5)]
                    param_lists.append(values)

        trials = []
        best_value = float('inf') if self.config.direction == "minimize" else float('-inf')
        best_params = None

        for param_values in itertools.product(*param_lists):
            params = dict(zip(param_names, param_values))
            try:
                value = train_function(params)
                trials.append({"params": params, "value": value})

                if self.config.direction == "minimize":
                    if value < best_value:
                        best_value = value
                        best_params = params
                else:
                    if value > best_value:
                        best_value = value
                        best_params = params

                # Check for early stopping
                if self._should_stop_early(best_value):
                    break
            except Exception as e:
                # Log the error but continue with other trials
                from autotrain import logger
                logger.error(f"Trial failed with params {params}: {str(e)}")
                # Optionally add failed trial with None value
                trials.append({"params": params, "value": None, "error": str(e)})

        return SweepResult(
            best_params=best_params,
            best_value=best_value,
            trials=trials,
            backend="grid_search"
        )


def run_autotrain_sweep(
    model_config: Dict,
    sweep_parameters: Dict,
    train_function: Callable,
    metric: str = "eval_loss",
    direction: str = "minimize",
    n_trials: int = 10,
    backend: str = "optuna",
    output_dir: Optional[str] = None,
) -> SweepResult:
    """
    Convenience function to run hyperparameter sweep for AutoTrain.

    Args:
        model_config: Base configuration dict
        sweep_parameters: Parameters to sweep with their ranges
        train_function: Function that takes params and returns metric value
        metric: Metric to optimize
        direction: "minimize" or "maximize"
        n_trials: Number of trials to run
        backend: Sweep backend to use
        output_dir: Directory to save results

    Returns:
        SweepResult with best parameters and trial history
    """
    # Convert sweep parameters to ParameterRange objects
    processed_params = {}
    for name, spec in sweep_parameters.items():
        if isinstance(spec, tuple) and len(spec) == 3:
            low, high, dist = spec
            processed_params[name] = ParameterRange(low, high, dist)
        elif isinstance(spec, list):
            processed_params[name] = spec
        else:
            processed_params[name] = spec

    # Handle backend aliases for backward compatibility
    backend_aliases = {
        'random': 'random_search',
        'grid': 'grid_search',
        'ray': 'ray_tune',
    }
    backend_normalized = backend.lower()
    backend_normalized = backend_aliases.get(backend_normalized, backend_normalized)

    config = SweepConfig(
        backend=SweepBackend(backend_normalized),
        n_trials=n_trials,
        direction=direction,
        parameters=processed_params,
        metric=metric,
    )

    sweep = HyperparameterSweep(config)
    result = sweep.run(train_function)

    # Save results if output_dir provided
    if output_dir:
        import json
        import os
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "sweep_results.json"), "w") as f:
            json.dump({
                "best_params": result.best_params,
                "best_value": result.best_value,
                "trials": result.trials,
            }, f, indent=2)

    return result


__all__ = [
    "get_model_loading_kwargs",
    "maybe_move_to_mps",
    "SweepBackend",
    "ParameterRange",
    "SweepConfig",
    "SweepResult",
    "HyperparameterSweep",
    "run_autotrain_sweep",
]


# Back-compat: run_training utility (used by CLI/backends/endpoints)
import json
import os
import subprocess
import sys
import threading


def run_training(params, task_id, local: bool = False, wait: bool = False) -> int:
    """
    Launch a training subprocess based on the provided parameters and task ID.

    Mirrors the original implementation from `autotrain.utils` (module form),
    kept here for compatibility after consolidation to a package.
    """
    # Lazy imports to avoid heavy module loading at package import time
    from autotrain.commands import launch_command
    from autotrain.trainers.clm.params import LLMTrainingParams
    from autotrain.trainers.extractive_question_answering.params import ExtractiveQuestionAnsweringParams
    from autotrain.trainers.generic.params import GenericParams
    from autotrain.trainers.image_classification.params import ImageClassificationParams
    from autotrain.trainers.image_regression.params import ImageRegressionParams
    from autotrain.trainers.object_detection.params import ObjectDetectionParams
    from autotrain.trainers.sent_transformers.params import SentenceTransformersParams
    from autotrain.trainers.seq2seq.params import Seq2SeqParams
    from autotrain.trainers.tabular.params import TabularParams
    from autotrain.trainers.text_classification.params import TextClassificationParams
    from autotrain.trainers.text_regression.params import TextRegressionParams
    from autotrain.trainers.token_classification.params import TokenClassificationParams
    from autotrain.trainers.vlm.params import VLMTrainingParams

    # Parse params
    params = json.loads(params)
    if isinstance(params, str):
        params = json.loads(params)
    if task_id == 9:
        params = LLMTrainingParams(**params)
    elif task_id == 28:
        params = Seq2SeqParams(**params)
    elif task_id in (1, 2):
        params = TextClassificationParams(**params)
    elif task_id in (13, 14, 15, 16, 26):
        params = TabularParams(**params)
    elif task_id == 27:
        params = GenericParams(**params)
    elif task_id == 18:
        params = ImageClassificationParams(**params)
    elif task_id == 4:
        params = TokenClassificationParams(**params)
    elif task_id == 10:
        params = TextRegressionParams(**params)
    elif task_id == 29:
        params = ObjectDetectionParams(**params)
    elif task_id == 30:
        params = SentenceTransformersParams(**params)
    elif task_id == 24:
        params = ImageRegressionParams(**params)
    elif task_id == 31:
        params = VLMTrainingParams(**params)
    elif task_id == 5:
        params = ExtractiveQuestionAnsweringParams(**params)
    else:
        raise NotImplementedError

    params.save(output_dir=params.project_name)
    env = os.environ.copy()

    # Ensure project log exists BEFORE building command to capture early hangs
    os.makedirs(params.project_name, exist_ok=True)
    log_path = os.path.join(params.project_name, "autotrain.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n=== Preparing training at {os.getcwd()} ===\n")
        f.write(f"Python path: {sys.executable}\n")
        f.write(f"PATH(pre): {env.get('PATH', 'Not set')}\n")
        f.write(f"PYTHONPATH(pre): {env.get('PYTHONPATH', 'Not set')}\n")
        f.write("Will compute launch command next...\n")
        f.flush()

    # Set GPU count override BEFORE building command to avoid torch/CUDA init in parent
    if "AUTOTRAIN_FORCE_NUM_GPUS" not in os.environ:
        forced = "1" if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", "-1") else "0"
        os.environ["AUTOTRAIN_FORCE_NUM_GPUS"] = forced

    cmd = [str(c) for c in launch_command(params=params)]

    # Try to locate accelerate in typical locations if needed
    import shutil
    venv_bin = "/app/.venv/bin"
    if os.path.exists(venv_bin) and venv_bin not in env.get("PATH", ""):
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '/usr/local/bin:/usr/bin:/bin')}"
    accelerate_path = shutil.which("accelerate", path=env.get("PATH"))
    if not accelerate_path:
        for path in (
            "/app/.venv/bin/accelerate",
            "/home/bentoml/.local/bin/accelerate",
            "/usr/local/bin/accelerate",
            os.path.expanduser("~/.local/bin/accelerate"),
        ):
            if os.path.exists(path):
                accelerate_path = path
                break
    if accelerate_path and cmd and cmd[0] == "accelerate":
        cmd[0] = accelerate_path

    # Ensure unbuffered Python output
    env.setdefault("PYTHONUNBUFFERED", "1")

    # Validate training config presence
    training_config_path = os.path.join(params.project_name, "training_params.json")
    if not os.path.isfile(training_config_path):
        raise FileNotFoundError(f"training_params.json not found at {training_config_path}")

    # Open log file for subprocess I/O
    log_fh = open(log_path, "a", encoding="utf-8")

    # Optionally force Python module launch instead of accelerate
    force_python = os.environ.get("AUTOTRAIN_FORCE_PYTHON_LAUNCH", "false").lower() in ("1", "true", "yes")
    if force_python and "-m" in cmd:
        try:
            m_index = cmd.index("-m")
            module = cmd[m_index + 1]
            module_args = cmd[m_index + 2:]
            cmd = [sys.executable, "-m", module] + module_args
        except Exception:
            pass

    # Launch training subprocess
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            close_fds=True,
            start_new_session=True,
        )
        # Reap in the background when wait=False
        def _reap_proc(p: subprocess.Popen, fh):
            try:
                exit_code = p.wait()
                try:
                    fh.write(f"\n=== Training subprocess exited with code {exit_code} ===\n")
                    fh.flush()
                except Exception:
                    pass
            finally:
                try:
                    fh.close()
                except Exception:
                    pass

        if not wait:
            threading.Thread(target=_reap_proc, args=(process, log_fh), daemon=True).start()
    except (FileNotFoundError, PermissionError, OSError) as spawn_err:
        # Try Python fallback if accelerate spawn fails
        fallback_cmd = None
        if (not accelerate_path) or (cmd and os.path.basename(cmd[0]).startswith("accelerate")):
            try:
                if "-m" in cmd:
                    m_index = cmd.index("-m")
                    module = cmd[m_index + 1]
                    module_args = cmd[m_index + 2:]
                    fallback_cmd = [sys.executable, "-m", module] + module_args
            except Exception:
                fallback_cmd = None

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"Primary launch failed: {spawn_err}\n")
            if fallback_cmd:
                f.write(f"Attempting Python fallback: {' '.join(fallback_cmd)}\n")

        if fallback_cmd:
            process = subprocess.Popen(
                fallback_cmd,
                env=env,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                close_fds=True,
                start_new_session=True,
            )
            if not wait:
                threading.Thread(target=_reap_proc, args=(process, log_fh), daemon=True).start()
        else:
            raise

    # Optionally wait for completion
    if wait:
        exit_code = process.wait()
        if exit_code != 0:
            raise RuntimeError(f"Training failed with exit code: {exit_code}")
    return process.pid
