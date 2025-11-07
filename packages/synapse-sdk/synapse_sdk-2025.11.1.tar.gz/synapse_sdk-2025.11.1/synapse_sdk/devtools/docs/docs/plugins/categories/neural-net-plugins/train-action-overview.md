---
id: train-action-overview
title: Train Action Overview
sidebar_position: 1
---

# Train Action Overview

The Train Action provides unified functionality for both model training and hyperparameter optimization (HPO) through a single interface. It supports regular training workflows and advanced hyperparameter tuning with Ray Tune integration.

## Quick Overview

**Category:** Neural Net
**Available Actions:** `train`
**Execution Method:** Job-based execution
**Modes:** Training mode and Hyperparameter Tuning mode

## Key Features

- **Unified Interface**: Single action for both training and hyperparameter tuning
- **Flexible Hyperparameters**: No rigid structure - plugins define their own hyperparameter schema
- **Ray Tune Integration**: Advanced HPO with multiple search algorithms and schedulers
- **Automatic Trial Tracking**: Trial IDs automatically injected into logs during tuning
- **Resource Management**: Configurable CPU/GPU allocation per trial
- **Best Model Selection**: Automatic best model checkpoint selection after tuning
- **Progress Tracking**: Real-time progress updates across training/tuning phases

## Modes

### Training Mode (Default)

Standard model training with fixed hyperparameters.

```json
{
  "action": "train",
  "params": {
    "name": "my_model",
    "dataset": 123,
    "checkpoint": null,
    "is_tune": false,
    "hyperparameter": {
      "epochs": 100,
      "batch_size": 32,
      "learning_rate": 0.001,
      "optimizer": "adam"
    }
  }
}
```

### Hyperparameter Tuning Mode

Hyperparameter optimization using Ray Tune.

```json
{
  "action": "train",
  "params": {
    "name": "my_tuning_job",
    "dataset": 123,
    "checkpoint": null,
    "is_tune": true,
    "tune_hyperparameter": [
      {
        "name": "batch_size",
        "type": "choice",
        "options": [16, 32, 64]
      },
      {
        "name": "learning_rate",
        "type": "loguniform",
        "min": 0.0001,
        "max": 0.01,
        "base": 10
      },
      {
        "name": "optimizer",
        "type": "choice",
        "options": ["adam", "sgd"]
      }
    ],
    "tune_config": {
      "mode": "max",
      "metric": "accuracy",
      "num_samples": 10,
      "max_concurrent_trials": 2
    }
  }
}
```

## Configuration Parameters

### Common Parameters (Both Modes)

| Parameter    | Type          | Required | Description                           |
| ------------ | ------------- | -------- | ------------------------------------- |
| `name`       | `str`         | Yes      | Training/tuning job name              |
| `dataset`    | `int`         | Yes      | Dataset ID                            |
| `checkpoint` | `int \| None` | No       | Checkpoint ID for resuming training   |
| `is_tune`    | `bool`        | No       | Enable tuning mode (default: `false`) |
| `num_cpus`   | `float`       | No       | CPU resources per trial (tuning only) |
| `num_gpus`   | `float`       | No       | GPU resources per trial (tuning only) |

### Training Mode Parameters (`is_tune=false`)

| Parameter        | Type   | Required | Description                        |
| ---------------- | ------ | -------- | ---------------------------------- |
| `hyperparameter` | `dict` | Yes      | Fixed hyperparameters for training |

**Note**: The structure of `hyperparameter` is completely flexible and defined by your plugin. Common fields include:

- `epochs`: Number of training epochs
- `batch_size`: Batch size for training
- `learning_rate`: Learning rate
- `optimizer`: Optimizer type (adam, sgd, etc.)
- Any custom fields your plugin needs (e.g., `dropout_rate`, `weight_decay`, `image_size`)

### Tuning Mode Parameters (`is_tune=true`)

| Parameter             | Type   | Required | Description                          |
| --------------------- | ------ | -------- | ------------------------------------ |
| `tune_hyperparameter` | `list` | Yes      | List of hyperparameter search spaces |
| `tune_config`         | `dict` | Yes      | Ray Tune configuration               |

## Hyperparameter Search Spaces

Define hyperparameter distributions for tuning:

### Continuous Distributions

```json
[
  {
    "name": "learning_rate",
    "type": "uniform",
    "min": 0.0001,
    "max": 0.01
  },
  {
    "name": "dropout_rate",
    "type": "loguniform",
    "min": 0.0001,
    "max": 0.1,
    "base": 10
  }
]
```

### Discrete Distributions

```json
[
  {
    "name": "batch_size",
    "type": "choice",
    "options": [16, 32, 64, 128]
  },
  {
    "name": "optimizer",
    "type": "choice",
    "options": ["adam", "sgd", "rmsprop"]
  }
]
```

### Quantized Distributions

```json
[
  {
    "name": "learning_rate",
    "type": "quniform",
    "min": 0.0001,
    "max": 0.01,
    "q": 0.0001
  }
]
```

### Supported Distribution Types

Each hyperparameter type requires specific parameters:

| Type | Required Parameters | Description | Example |
|------|-------------------|-------------|---------|
| `uniform` | `min`, `max` | Uniform distribution between min and max | `{"name": "lr", "type": "uniform", "min": 0.0001, "max": 0.01}` |
| `quniform` | `min`, `max` | Quantized uniform distribution | `{"name": "lr", "type": "quniform", "min": 0.0001, "max": 0.01}` |
| `loguniform` | `min`, `max`, `base` | Log-uniform distribution | `{"name": "lr", "type": "loguniform", "min": 0.0001, "max": 0.01, "base": 10}` |
| `qloguniform` | `min`, `max`, `base` | Quantized log-uniform distribution | `{"name": "lr", "type": "qloguniform", "min": 0.0001, "max": 0.01, "base": 10}` |
| `randn` | `mean`, `sd` | Normal (Gaussian) distribution | `{"name": "noise", "type": "randn", "mean": 0.0, "sd": 1.0}` |
| `qrandn` | `mean`, `sd` | Quantized normal distribution | `{"name": "noise", "type": "qrandn", "mean": 0.0, "sd": 1.0}` |
| `randint` | `min`, `max` | Random integer between min and max | `{"name": "epochs", "type": "randint", "min": 5, "max": 15}` |
| `qrandint` | `min`, `max` | Quantized random integer | `{"name": "epochs", "type": "qrandint", "min": 5, "max": 15}` |
| `lograndint` | `min`, `max`, `base` | Log-random integer | `{"name": "units", "type": "lograndint", "min": 16, "max": 256, "base": 2}` |
| `qlograndint` | `min`, `max`, `base` | Quantized log-random integer | `{"name": "units", "type": "qlograndint", "min": 16, "max": 256, "base": 2}` |
| `choice` | `options` | Choose from a list of values | `{"name": "optimizer", "type": "choice", "options": ["adam", "sgd"]}` |
| `grid_search` | `options` | Grid search over all values | `{"name": "batch_size", "type": "grid_search", "options": [16, 32, 64]}` |

**Important Notes:**
- All hyperparameters must include `name` and `type` fields
- For `loguniform`, `qloguniform`, `lograndint`, `qlograndint`: `base` parameter is required (typically 10 or 2)
- For `choice` and `grid_search`: Use `options` (not `values`)
- For range-based types: Use `min` and `max` (not `lower` and `upper`)

## Tune Configuration

### Basic Configuration

```python
{
  "mode": "max",              # "max" or "min"
  "metric": "accuracy",       # Metric to optimize
  "num_samples": 10,          # Number of trials
  "max_concurrent_trials": 2  # Parallel trials
}
```

### With Search Algorithm

```python
{
  "mode": "max",
  "metric": "accuracy",
  "num_samples": 20,
  "max_concurrent_trials": 4,
  "search_alg": {
    "name": "hyperoptsearch",   # Search algorithm
    "points_to_evaluate": [     # Optional initial points
      {
        "learning_rate": 0.001,
        "batch_size": 32
      }
    ]
  }
}
```

### With Scheduler

```python
{
  "mode": "max",
  "metric": "accuracy",
  "num_samples": 50,
  "max_concurrent_trials": 8,
  "scheduler": {
    "name": "hyperband",        # Scheduler type
    "options": {
      "max_t": 100
    }
  }
}
```

### Supported Search Algorithms

- `basicvariantgenerator` - Random search (default)
- `bayesoptsearch` - Bayesian optimization
- `hyperoptsearch` - Tree-structured Parzen Estimator

### Supported Schedulers

- `fifo` - First-in-first-out (default)
- `hyperband` - HyperBand scheduler

## Plugin Development

### For Training Mode

Implement the `train()` function in your plugin:

```python
def train(run, dataset, hyperparameter, checkpoint, **kwargs):
    """
    Training function for your model.

    Args:
        run: TrainRun object for logging
        dataset: Dataset object
        hyperparameter: dict with hyperparameters
        checkpoint: Optional checkpoint for resuming
    """
    # Access hyperparameters
    epochs = hyperparameter['epochs']
    batch_size = hyperparameter['batch_size']
    learning_rate = hyperparameter['learning_rate']

    # Training loop
    for epoch in range(epochs):
        # Train one epoch
        loss, accuracy = train_one_epoch(...)

        # Log metrics
        run.log_metric('training', 'loss', loss, epoch=epoch)
        run.log_metric('training', 'accuracy', accuracy, epoch=epoch)

        # Log visualizations
        run.log_visualization('predictions', 'train', epoch, image_data)

    # Save final model
    save_model(model, '/path/to/model.pth')
```

### For Tuning Mode

Implement the `tune()` function in your plugin:

```python
def tune(hyperparameter, run, dataset, checkpoint, **kwargs):
    """
    Tuning function for hyperparameter optimization.

    Args:
        hyperparameter: dict with current trial's hyperparameters
        run: TrainRun object for logging (with is_tune=True)
        dataset: Dataset object
        checkpoint: Optional checkpoint for resuming
    """
    from ray import tune

    # Set checkpoint output path BEFORE training
    output_path = Path('/path/to/trial/weights')
    run.checkpoint_output = str(output_path)

    # Training loop
    for epoch in range(hyperparameter['epochs']):
        loss, accuracy = train_one_epoch(...)

        # Log metrics (trial_id automatically added)
        run.log_metric('training', 'loss', loss, epoch=epoch)
        run.log_metric('training', 'accuracy', accuracy, epoch=epoch)

    # Report results to Ray Tune
    results = {
        "accuracy": final_accuracy,
        "loss": final_loss
    }

    # IMPORTANT: Report with checkpoint
    tune.report(
        results,
        checkpoint=tune.Checkpoint.from_directory(run.checkpoint_output)
    )
```

### Parameter Order Difference

**Important**: The parameter order differs between `train()` and `tune()`:

- `train(run, dataset, hyperparameter, checkpoint, **kwargs)`
- `tune(hyperparameter, run, dataset, checkpoint, **kwargs)`

### Automatic Trial ID Logging

When `is_tune=True`, the SDK automatically injects `trial_id` into all metric and visualization logs:

```python
# Your plugin code
run.log_metric('training', 'loss', 0.5, epoch=10)

# Actual logged data (trial_id added automatically)
{
  'category': 'training',
  'key': 'loss',
  'value': 0.5,
  'metrics': {'epoch': 10},
  'trial_id': 'abc123'  # Added automatically
}
```

No plugin changes required - this happens transparently at the SDK level.

## Migration from TuneAction

The standalone `TuneAction` is now **deprecated**. Migrate to `TrainAction` with `is_tune=true`:

### Before (Deprecated)

```json
{
  "action": "tune",
  "params": {
    "name": "my_tuning_job",
    "dataset": 123,
    "hyperparameter": [...],
    "tune_config": {...}
  }
}
```

### After (Recommended)

```json
{
  "action": "train",
  "params": {
    "name": "my_tuning_job",
    "dataset": 123,
    "is_tune": true,
    "tune_hyperparameter": [...],
    "tune_config": {...}
  }
}
```

### Key Changes

1. Change `"action": "tune"` to `"action": "train"`
2. Add `"is_tune": true`
3. Rename `"hyperparameter"` to `"tune_hyperparameter"`

## Examples

### Simple Training

```json
{
  "action": "train",
  "params": {
    "name": "resnet50_training",
    "dataset": 456,
    "checkpoint": null,
    "hyperparameter": {
      "epochs": 100,
      "batch_size": 32,
      "learning_rate": 0.001,
      "optimizer": "adam",
      "weight_decay": 0.0001
    }
  }
}
```

### Resume from Checkpoint

```json
{
  "action": "train",
  "params": {
    "name": "resnet50_continued",
    "dataset": 456,
    "checkpoint": 789,
    "hyperparameter": {
      "epochs": 50,
      "batch_size": 32,
      "learning_rate": 0.0001,
      "optimizer": "adam"
    }
  }
}
```

### Hyperparameter Tuning with Grid Search

```json
{
  "action": "train",
  "params": {
    "name": "resnet50_tuning",
    "dataset": 456,
    "is_tune": true,
    "tune_hyperparameter": [
      {
        "name": "batch_size",
        "type": "grid_search",
        "options": [16, 32, 64]
      },
      {
        "name": "learning_rate",
        "type": "grid_search",
        "options": [0.001, 0.0001]
      },
      {
        "name": "optimizer",
        "type": "grid_search",
        "options": ["adam", "sgd"]
      }
    ],
    "tune_config": {
      "mode": "max",
      "metric": "validation_accuracy",
      "num_samples": 12,
      "max_concurrent_trials": 4
    }
  }
}
```

### Advanced Tuning with HyperOpt and HyperBand

```json
{
  "action": "train",
  "params": {
    "name": "resnet50_hyperopt_tuning",
    "dataset": 456,
    "is_tune": true,
    "num_cpus": 2,
    "num_gpus": 0.5,
    "tune_hyperparameter": [
      {
        "name": "batch_size",
        "type": "choice",
        "options": [16, 32, 64, 128]
      },
      {
        "name": "learning_rate",
        "type": "loguniform",
        "min": 0.00001,
        "max": 0.01,
        "base": 10
      },
      {
        "name": "weight_decay",
        "type": "loguniform",
        "min": 0.00001,
        "max": 0.001,
        "base": 10
      },
      {
        "name": "optimizer",
        "type": "choice",
        "options": ["adam", "sgd", "rmsprop"]
      }
    ],
    "tune_config": {
      "mode": "max",
      "metric": "validation_accuracy",
      "num_samples": 50,
      "max_concurrent_trials": 8,
      "search_alg": {
        "name": "hyperoptsearch"
      },
      "scheduler": {
        "name": "hyperband",
        "options": {
          "max_t": 100
        }
      }
    }
  }
}
```

## Progress Tracking

The train action tracks progress across different phases:

### Training Mode

| Category     | Proportion | Description          |
| ------------ | ---------- | -------------------- |
| `validation` | 10%        | Parameter validation |
| `training`   | 90%        | Model training       |

### Tuning Mode

| Category     | Proportion | Description                  |
| ------------ | ---------- | ---------------------------- |
| `validation` | 10%        | Parameter validation         |
| `trials`     | 90%        | Hyperparameter tuning trials |

## Benefits

### Unified Interface

- Single action for both training and tuning
- Consistent parameter handling
- Reduced code duplication

### Flexible Hyperparameters

- No rigid structure enforced by SDK
- Plugins define their own hyperparameter schema
- Support for custom fields without validation errors

### Advanced HPO

- Multiple search algorithms (Optuna, Ax, HyperOpt, BayesOpt)
- Multiple schedulers (ASHA, HyperBand, PBT)
- Automatic best model selection

### Developer Experience

- Automatic trial tracking
- Transparent logging enhancements
- Clear migration path from deprecated TuneAction

## Best Practices

### Hyperparameter Design

- Keep hyperparameter search spaces reasonable
- Start with grid search for initial exploration
- Use Bayesian optimization (Optuna, Ax) for efficient search
- Set appropriate `num_samples` based on search space size

### Resource Management

- Allocate `num_cpus` and `num_gpus` based on trial resource needs
- Set `max_concurrent_trials` based on available hardware
- Monitor resource usage during tuning

### Checkpoint Management

- Always set `run.checkpoint_output` before training in tune mode
- Save checkpoints at regular intervals
- Use the best checkpoint returned by tuning

### Logging

- Log all relevant metrics for comparison
- Use consistent metric names across trials
- Include validation metrics in tune reports

## Troubleshooting

### Common Issues

#### "hyperparameter is required when is_tune=False"

Make sure to provide `hyperparameter` in training mode:

```json
{
  "is_tune": false,
  "hyperparameter": {...}
}
```

#### "tune_hyperparameter is required when is_tune=True"

Make sure to provide `tune_hyperparameter` and `tune_config` in tuning mode:

```json
{
  "is_tune": true,
  "tune_hyperparameter": [...],
  "tune_config": {...}
}
```

#### Tuning Fails Without Error

Check that your `tune()` function:

1. Sets `run.checkpoint_output` before training
2. Calls `tune.report()` with results and checkpoint
3. Returns properly without exceptions

## Next Steps

- **For Plugin Developers**: Implement `train()` and optionally `tune()` functions
- **For Users**: Start with training mode, then experiment with tuning
- **For Advanced Users**: Explore different search algorithms and schedulers

## Support and Resources

- **API Reference**: See TrainAction class documentation
- **Examples**: Check plugin examples repository
- **Ray Tune Documentation**: https://docs.ray.io/en/latest/tune/
