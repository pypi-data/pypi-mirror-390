import copy
import tempfile
from pathlib import Path
from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, field_validator, model_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.models import Run
from synapse_sdk.utils.file import archive, get_temp_path, unarchive
from synapse_sdk.utils.module_loading import import_string
from synapse_sdk.utils.pydantic.validators import non_blank


class TrainRun(Run):
    is_tune = False
    completed_samples = 0
    num_samples = 0
    checkpoint_output = None

    def log_metric(self, category, key, value, **metrics):
        # TODO validate input via plugin config
        data = {'category': category, 'key': key, 'value': value, 'metrics': metrics}

        # Automatically add trial_id when is_tune=True
        if self.is_tune:
            try:
                from ray import train

                context = train.get_context()
                trial_id = context.get_trial_id()
                if trial_id:
                    data['trial_id'] = trial_id
            except Exception:
                # If Ray context is not available, continue without trial_id
                pass

        self.log('metric', data)

    def log_visualization(self, category, group, index, image, **meta):
        # TODO validate input via plugin config
        data = {'category': category, 'group': group, 'index': index, **meta}

        # Automatically add trial_id when is_tune=True
        if self.is_tune:
            try:
                from ray import train

                context = train.get_context()
                trial_id = context.get_trial_id()
                if trial_id:
                    data['trial_id'] = trial_id
            except Exception:
                # If Ray context is not available, continue without trial_id
                pass

        self.log('visualization', data, file=image)


class SearchAlgo(BaseModel):
    """
    Configuration for Ray Tune search algorithms.

    Supported algorithms:
        - 'bayesoptsearch': Bayesian optimization using Gaussian Processes
        - 'hyperoptsearch': Tree-structured Parzen Estimator (TPE)
        - 'basicvariantgenerator': Random search (default)

    Attributes:
        name (str): Name of the search algorithm (case-insensitive)
        points_to_evaluate (Optional[dict]): Optional initial hyperparameter
            configurations to evaluate before starting optimization

    Example:
        {
            "name": "hyperoptsearch",
            "points_to_evaluate": [
                {"learning_rate": 0.001, "batch_size": 32}
            ]
        }
    """

    name: str
    points_to_evaluate: Optional[dict] = None


class Scheduler(BaseModel):
    """
    Configuration for Ray Tune schedulers.

    Supported schedulers:
        - 'fifo': First-In-First-Out scheduler (default, runs all trials)
        - 'hyperband': HyperBand early stopping scheduler

    Attributes:
        name (str): Name of the scheduler (case-insensitive)
        options (Optional[str]): Optional scheduler-specific configuration parameters

    Example:
        {
            "name": "hyperband",
            "options": {
                "max_t": 100,
                "reduction_factor": 3
            }
        }
    """

    name: str
    options: Optional[str] = None


class TuneConfig(BaseModel):
    """
    Configuration for Ray Tune hyperparameter optimization.

    Used when is_tune=True to configure the hyperparameter search process.

    Attributes:
        mode (Optional[str]): Optimization mode - 'max' or 'min'
        metric (Optional[str]): Name of the metric to optimize
        num_samples (int): Number of hyperparameter configurations to try (default: 1)
        max_concurrent_trials (Optional[int]): Maximum number of trials to run in parallel
        search_alg (Optional[SearchAlgo]): Search algorithm configuration
        scheduler (Optional[Scheduler]): Trial scheduler configuration

    Example:
        {
            "mode": "max",
            "metric": "accuracy",
            "num_samples": 20,
            "max_concurrent_trials": 4,
            "search_alg": {
                "name": "hyperoptsearch"
            },
            "scheduler": {
                "name": "hyperband",
                "options": {"max_t": 100}
            }
        }
    """

    mode: Optional[str] = None
    metric: Optional[str] = None
    num_samples: int = 1
    max_concurrent_trials: Optional[int] = None
    search_alg: Optional[SearchAlgo] = None
    scheduler: Optional[Scheduler] = None


class TrainParams(BaseModel):
    """
    Parameters for TrainAction supporting both regular training and hyperparameter tuning.

    Attributes:
        name (str): Name for the training/tuning job
        description (str): Description of the job
        checkpoint (int | None): Optional checkpoint ID to resume from
        dataset (int): Dataset ID to use for training
        is_tune (bool): Enable hyperparameter tuning mode (default: False)
        tune_config (Optional[TuneConfig]): Tune configuration (required when is_tune=True)
        num_cpus (Optional[int]): CPUs per trial (tuning mode only)
        num_gpus (Optional[int]): GPUs per trial (tuning mode only)
        hyperparameter (Optional[Any]): Fixed hyperparameters (required when is_tune=False)
        hyperparameters (Optional[list]): Hyperparameter search space (required when is_tune=True)

    Hyperparameter format when is_tune=True:
        Each item in hyperparameters list must have:
        - 'name': Parameter name (string)
        - 'type': Distribution type (string)
        - Type-specific parameters:
            - uniform/quniform: 'min', 'max'
            - loguniform/qloguniform: 'min', 'max', 'base'
            - randn/qrandn: 'mean', 'sd'
            - randint/qrandint: 'min', 'max'
            - lograndint/qlograndint: 'min', 'max', 'base'
            - choice/grid_search: 'options'

    Example (Training mode):
        {
            "name": "my_training",
            "dataset": 123,
            "is_tune": false,
            "hyperparameter": {
                "epochs": 100,
                "batch_size": 32,
                "learning_rate": 0.001
            }
        }

    Example (Tuning mode):
        {
            "name": "my_tuning",
            "dataset": 123,
            "is_tune": true,
            "hyperparameters": [
                {"name": "batch_size", "type": "choice", "options": [16, 32, 64]},
                {"name": "learning_rate", "type": "loguniform", "min": 0.0001, "max": 0.01, "base": 10},
                {"name": "epochs", "type": "randint", "min": 5, "max": 15}
            ],
            "tune_config": {
                "mode": "max",
                "metric": "accuracy",
                "num_samples": 10
            }
        }
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str
    checkpoint: int | None
    dataset: int
    is_tune: bool = False
    tune_config: Optional[TuneConfig] = None
    num_cpus: Optional[int] = None
    num_gpus: Optional[int] = None
    hyperparameter: Optional[dict] = None  # plan to be deprecated
    hyperparameters: Optional[list] = None

    @field_validator('hyperparameter', mode='before')
    @classmethod
    def validate_hyperparameter(cls, v, info):
        """Validate hyperparameter for train mode (is_tune=False)"""
        # Get is_tune flag to determine if this field should be validated
        is_tune = info.data.get('is_tune', False)

        # If is_tune=True, hyperparameter should be None/not used
        # Just return whatever was passed (will be validated in model_validator)
        if is_tune:
            return v

        # For train mode, hyperparameter should be a dict
        if isinstance(v, dict):
            return v
        elif isinstance(v, list):
            raise ValueError(
                'hyperparameter must be a dict, not a list. '
                'If you want to use hyperparameter tuning, '
                'set "is_tune": true and use "hyperparameters" instead.'
            )
        else:
            raise ValueError('hyperparameter must be a dict')

    @field_validator('hyperparameters', mode='before')
    @classmethod
    def validate_hyperparameters(cls, v, info):
        """Validate hyperparameters for tune mode (is_tune=True)"""
        # Get is_tune flag to determine if this field should be validated
        is_tune = info.data.get('is_tune', False)

        # If is_tune=False, hyperparameters should be None/not used
        # Just return whatever was passed (will be validated in model_validator)
        if not is_tune:
            return v

        # For tune mode, hyperparameters should be a list
        if isinstance(v, list):
            return v
        elif isinstance(v, dict):
            raise ValueError(
                'hyperparameters must be a list, not a dict. '
                'If you want to use fixed hyperparameters for training, '
                'set "is_tune": false and use "hyperparameter" instead.'
            )
        else:
            raise ValueError('hyperparameters must be a list')

    @field_validator('name')
    @staticmethod
    def unique_name(value, info):
        action = info.context['action']
        client = action.client
        is_tune = info.data.get('is_tune', False)
        try:
            if not is_tune:
                model_exists = client.exists('list_models', params={'name': value})
                job_exists = client.exists(
                    'list_jobs',
                    params={
                        'ids_ex': action.job_id,
                        'category': 'neural_net',
                        'job__action': 'train',
                        'is_active': True,
                        'params': f'name:{value.replace(":", "%3A")}',
                    },
                )
                assert not model_exists and not job_exists, '존재하는 학습 이름입니다.'
            else:
                job_exists = client.exists(
                    'list_jobs',
                    params={
                        'ids_ex': action.job_id,
                        'category': 'neural_net',
                        'job__action': 'train',
                        'is_active': True,
                        'params': f'name:{value}',
                    },
                )
                assert not job_exists, '존재하는 튜닝 작업 이름입니다.'
        except ClientError:
            raise PydanticCustomError('client_error', '')
        return value

    @model_validator(mode='after')
    def validate_tune_params(self):
        if self.is_tune:
            # When is_tune=True, hyperparameters is required
            if self.hyperparameters is None:
                raise ValueError('hyperparameters is required when is_tune=True')
            if self.hyperparameter is not None:
                raise ValueError('hyperparameter should not be provided when is_tune=True, use hyperparameters instead')
            if self.tune_config is None:
                raise ValueError('tune_config is required when is_tune=True')
        else:
            # When is_tune=False, either hyperparameter or hyperparameters is required
            if self.hyperparameter is None and self.hyperparameters is None:
                raise ValueError('Either hyperparameter or hyperparameters is required when is_tune=False')

            if self.hyperparameter is not None and self.hyperparameters is not None:
                raise ValueError('Provide either hyperparameter or hyperparameters, but not both')

            if self.hyperparameters is not None:
                if not isinstance(self.hyperparameters, list) or len(self.hyperparameters) != 1:
                    raise ValueError('hyperparameters must be a list containing a single dictionary')
                self.hyperparameter = self.hyperparameters[0]
                self.hyperparameters = None
        return self


@register_action
class TrainAction(Action):
    """
    **Important notes when using train with is_tune=True:**

    1. Path to the model output (which is the return value of your train function)
       should be set to the checkpoint_output attribute of the run object **before**
       starting the training.
    2. Before exiting the training function, report the results to Tune.
    3. When using own tune.py, take note of the difference in the order of parameters.
       tune() function starts with hyperparameter, run, dataset, checkpoint, **kwargs
       whereas the train() function starts with run, dataset, hyperparameter, checkpoint, **kwargs.
    ----
    1)
    Set the output path for the checkpoint to export best model

    output_path = Path('path/to/your/weights')
    run.checkpoint_output = str(output_path)

    2)
    Before exiting the training function, report the results to Tune.
    The results_dict should contain the metrics you want to report.

    Example: (In train function)
    results_dict = {
        "accuracy": accuracy,
        "loss": loss,
        # Add other metrics as needed
    }
    if hasattr(self.dm_run, 'is_tune') and self.dm_run.is_tune:
        tune.report(results_dict, checkpoint=tune.Checkpoint.from_directory(self.dm_run.checkpoint_output))


    3)
    tune() function takes hyperparameter, run, dataset, checkpoint, **kwargs in that order
    whereas train() function takes run, dataset, hyperparameter, checkpoint, **kwargs in that order.

    """

    name = 'train'
    category = PluginCategory.NEURAL_NET
    method = RunMethod.JOB
    run_class = TrainRun
    params_model = TrainParams
    progress_categories = {
        'dataset': {
            'proportion': 20,
        },
        'train': {
            'proportion': 75,
        },
        'trials': {
            'proportion': 90,
        },
        'model_upload': {
            'proportion': 5,
        },
    }

    def start(self):
        if self.params.get('is_tune', False):
            return self._start_tune()
        else:
            return self._start_train()

    def _start_train(self):
        """Original train logic"""
        hyperparameter = self.params.get('hyperparameter')
        if hyperparameter is None:
            hyperparameter = self.params['hyperparameters'][0]

        # download dataset
        self.run.log_message('Preparing dataset for training.')
        input_dataset = self.get_dataset()

        # retrieve checkpoint
        checkpoint = None
        if self.params['checkpoint']:
            self.run.log_message('Retrieving checkpoint.')
            checkpoint = self.get_model(self.params['checkpoint'])

        # train dataset
        self.run.log_message('Starting model training.')
        result = self.entrypoint(self.run, input_dataset, hyperparameter, checkpoint=checkpoint)

        # upload model_data
        self.run.log_message('Registering model data.')
        self.run.set_progress(0, 1, category='model_upload')
        model = self.create_model(result)
        self.run.set_progress(1, 1, category='model_upload')

        self.run.end_log()
        return {'model_id': model['id'] if model else None}

    def _start_tune(self):
        """Tune logic using Ray Tune for hyperparameter optimization"""
        from ray import tune

        # Mark run as tune
        self.run.is_tune = True

        # download dataset
        self.run.log_message('Preparing dataset for hyperparameter tuning.')
        input_dataset = self.get_dataset()

        # retrieve checkpoint
        checkpoint = None
        if self.params['checkpoint']:
            self.run.log_message('Retrieving checkpoint.')
            checkpoint = self.get_model(self.params['checkpoint'])

        # train dataset
        self.run.log_message('Starting training for hyperparameter tuning.')

        # Save num_samples to TrainRun for logging
        self.run.num_samples = self.params['tune_config']['num_samples']

        entrypoint = self.entrypoint
        if not self._tune_override_exists():
            # entrypoint must be train entrypoint
            def _tune(param_space, run, dataset, checkpoint=None, **kwargs):
                return entrypoint(run, dataset, param_space, checkpoint, **kwargs)

            entrypoint = _tune

        trainable = tune.with_parameters(entrypoint, run=self.run, dataset=input_dataset, checkpoint=checkpoint)

        tune_config = self.params['tune_config']

        # Extract search_alg and scheduler as separate objects to avoid JSON serialization issues
        search_alg = self.convert_tune_search_alg(tune_config)
        scheduler = self.convert_tune_scheduler(tune_config)

        # Create a copy of tune_config without non-serializable objects
        tune_config_dict = {
            'mode': tune_config.get('mode'),
            'metric': tune_config.get('metric'),
            'num_samples': tune_config.get('num_samples', 1),
            'max_concurrent_trials': tune_config.get('max_concurrent_trials'),
        }

        # Add search_alg and scheduler to tune_config_dict only if they exist
        if search_alg is not None:
            tune_config_dict['search_alg'] = search_alg
        if scheduler is not None:
            tune_config_dict['scheduler'] = scheduler

        hyperparameters = self.params['hyperparameters']
        param_space = self.convert_tune_params(hyperparameters)
        temp_path = tempfile.TemporaryDirectory()

        tuner = tune.Tuner(
            tune.with_resources(trainable, resources=self.tune_resources),
            tune_config=tune.TuneConfig(**tune_config_dict),
            run_config=tune.RunConfig(
                name=f'synapse_tune_hpo_{self.job_id}',
                log_to_file=('stdout.log', 'stderr.log'),
                storage_path=temp_path.name,
            ),
            param_space=param_space,
        )
        result = tuner.fit()

        best_result = result.get_best_result()

        # upload model_data
        self.run.log_message('Registering best model data.')
        self.run.set_progress(0, 1, category='model_upload')
        self.create_model_from_result(best_result)
        self.run.set_progress(1, 1, category='model_upload')

        self.run.end_log()

        return {'best_result': best_result.config}

    def get_dataset(self):
        client = self.run.client
        assert bool(client)

        input_dataset = {}

        ground_truths, count_dataset = client.list_ground_truth_events(
            params={
                'fields': ['category', 'files', 'data'],
                'expand': ['data'],
                'ground_truth_dataset_versions': self.params['dataset'],
            },
            list_all=True,
        )
        self.run.set_progress(0, count_dataset, category='dataset')
        for i, ground_truth in enumerate(ground_truths, start=1):
            self.run.set_progress(i, count_dataset, category='dataset')
            try:
                input_dataset[ground_truth['category']].append(ground_truth)
            except KeyError:
                input_dataset[ground_truth['category']] = [ground_truth]

        return input_dataset

    def get_model(self, model_id):
        model = self.client.get_model(model_id)
        model_file = Path(model['file'])
        output_path = get_temp_path(f'models/{model_file.stem}')
        if not output_path.exists():
            unarchive(model_file, output_path)
        model['path'] = output_path
        return model

    def create_model(self, path):
        params = copy.deepcopy(self.params)
        configuration_fields = ['hyperparameter']
        configuration = {field: params.pop(field) for field in configuration_fields}

        with tempfile.TemporaryDirectory() as temp_path:
            input_path = Path(path)
            archive_path = Path(temp_path, 'archive.zip')
            archive(input_path, archive_path)

            return self.client.create_model({
                'plugin': self.plugin_release.plugin,
                'version': self.plugin_release.version,
                'file': str(archive_path),
                'configuration': configuration,
                **params,
            })

    @property
    def tune_resources(self):
        resources = {}
        for option in ['num_cpus', 'num_gpus']:
            option_value = self.params.get(option)
            if option_value:
                # Remove the 'num_' prefix and trailing s from the option name
                resources[(lambda s: s[4:-1])(option)] = option_value
        return resources

    def create_model_from_result(self, result):
        params = copy.deepcopy(self.params)
        configuration_fields = ['hyperparameters']
        configuration = {field: params.pop(field) for field in configuration_fields}

        with tempfile.TemporaryDirectory() as temp_path:
            archive_path = Path(temp_path, 'archive.zip')

            # Archive tune results
            # https://docs.ray.io/en/latest/tune/tutorials/tune_get_data_in_and_out.html#getting-data-out-of-tune-using-checkpoints-other-artifacts
            archive(result.path, archive_path)

            return self.client.create_model({
                'plugin': self.plugin_release.plugin,
                'version': self.plugin_release.version,
                'file': str(archive_path),
                'configuration': configuration,
                **params,
            })

    @staticmethod
    def convert_tune_scheduler(tune_config):
        """
        Convert YAML hyperparameter configuration to a Ray Tune scheduler.

        Args:
            tune_config (dict): Hyperparameter configuration.

        Returns:
            object: Ray Tune scheduler instance.

        Supported schedulers:
            - 'fifo': FIFOScheduler (default)
            - 'hyperband': HyperBandScheduler
        """

        from ray.tune.schedulers import (
            ASHAScheduler,
            FIFOScheduler,
            HyperBandScheduler,
            MedianStoppingRule,
            PopulationBasedTraining,
        )

        if tune_config.get('scheduler') is None:
            return None

        scheduler_map = {
            'fifo': FIFOScheduler,
            'asha': ASHAScheduler,
            'hyperband': HyperBandScheduler,
            'pbt': PopulationBasedTraining,
            'median': MedianStoppingRule,
        }

        scheduler_type = tune_config['scheduler'].get('name', 'fifo').lower()
        scheduler_class = scheduler_map.get(scheduler_type, FIFOScheduler)

        # 옵션이 있는 경우 전달하고, 없으면 기본 생성자 호출
        options = tune_config['scheduler'].get('options')

        # options가 None이거나 빈 딕셔너리가 아닌 경우에만 전달
        scheduler = scheduler_class(**options) if options else scheduler_class()

        return scheduler

    @staticmethod
    def convert_tune_search_alg(tune_config):
        """
        Convert YAML hyperparameter configuration to Ray Tune search algorithm.

        Args:
            tune_config (dict): Hyperparameter configuration.

        Returns:
            object: Ray Tune search algorithm instance or None

        Supported search algorithms:
            - 'bayesoptsearch': Bayesian optimization
            - 'hyperoptsearch': Tree-structured Parzen Estimator
            - 'basicvariantgenerator': Random search (default)
        """

        if tune_config.get('search_alg') is None:
            return None

        search_alg_name = tune_config['search_alg']['name'].lower()
        metric = tune_config['metric']
        mode = tune_config['mode']
        points_to_evaluate = tune_config['search_alg'].get('points_to_evaluate', None)

        if search_alg_name == 'axsearch':
            from ray.tune.search.ax import AxSearch

            search_alg = AxSearch(metric=metric, mode=mode)
        elif search_alg_name == 'bayesoptsearch':
            from ray.tune.search.bayesopt import BayesOptSearch

            search_alg = BayesOptSearch(metric=metric, mode=mode)
        elif search_alg_name == 'hyperoptsearch':
            from ray.tune.search.hyperopt import HyperOptSearch

            search_alg = HyperOptSearch(metric=metric, mode=mode)
        elif search_alg_name == 'optunasearch':
            from ray.tune.search.optuna import OptunaSearch

            search_alg = OptunaSearch(metric=metric, mode=mode)
        elif search_alg_name == 'basicvariantgenerator':
            from ray.tune.search.basic_variant import BasicVariantGenerator

            search_alg = BasicVariantGenerator(points_to_evaluate=points_to_evaluate)
        else:
            raise ValueError(
                f'Unsupported search algorithm: {search_alg_name}. '
                f'Supported algorithms are: bayesoptsearch, hyperoptsearch, basicvariantgenerator'
            )

        return search_alg

    @staticmethod
    def convert_tune_params(param_list):
        """
        Convert YAML hyperparameter configuration to Ray Tune parameter dictionary.

        Args:
            param_list (list): List of hyperparameter configurations.

        Returns:
            dict: Ray Tune parameter dictionary
        """
        from ray import tune

        param_handlers = {
            'uniform': lambda p: tune.uniform(p['min'], p['max']),
            'quniform': lambda p: tune.quniform(p['min'], p['max']),
            'loguniform': lambda p: tune.loguniform(p['min'], p['max'], p['base']),
            'qloguniform': lambda p: tune.qloguniform(p['min'], p['max'], p['base']),
            'randn': lambda p: tune.randn(p['mean'], p['sd']),
            'qrandn': lambda p: tune.qrandn(p['mean'], p['sd']),
            'randint': lambda p: tune.randint(p['min'], p['max']),
            'qrandint': lambda p: tune.qrandint(p['min'], p['max']),
            'lograndint': lambda p: tune.lograndint(p['min'], p['max'], p['base']),
            'qlograndint': lambda p: tune.qlograndint(p['min'], p['max'], p['base']),
            'choice': lambda p: tune.choice(p['options']),
            'grid_search': lambda p: tune.grid_search(p['options']),
        }

        param_space = {}

        for param in param_list:
            name = param['name']
            param_type = param['type']

            if param_type in param_handlers:
                param_space[name] = param_handlers[param_type](param)
            else:
                raise ValueError(f'Unknown parameter type: {param_type}')

        return param_space

    @staticmethod
    def _tune_override_exists(module_path='plugin.tune') -> bool:
        try:
            import_string(module_path)
            return True
        except ImportError:
            return False
