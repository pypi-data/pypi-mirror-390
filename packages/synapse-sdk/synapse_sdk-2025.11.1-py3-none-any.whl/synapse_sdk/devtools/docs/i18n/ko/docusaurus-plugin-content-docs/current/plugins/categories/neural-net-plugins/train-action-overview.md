---
id: train-action-overview
title: Train 액션 개요
sidebar_position: 1
---

# Train 액션 개요

Train 액션은 단일 인터페이스를 통해 모델 학습과 하이퍼파라미터 최적화(HPO)를 모두 제공하는 통합 기능입니다. 일반 학습 워크플로우와 Ray Tune 통합을 통한 고급 하이퍼파라미터 튜닝을 지원합니다.

## 빠른 개요

**카테고리:** Neural Net
**사용 가능한 액션:** `train`
**실행 방식:** 작업 기반 실행
**모드:** 학습 모드 및 하이퍼파라미터 튜닝 모드

## 주요 기능

- **통합 인터페이스**: 학습과 하이퍼파라미터 튜닝을 위한 단일 액션
- **유연한 하이퍼파라미터**: 고정된 구조 없음 - 플러그인이 자체 하이퍼파라미터 스키마 정의
- **Ray Tune 통합**: 다양한 검색 알고리즘과 스케줄러를 통한 고급 HPO
- **자동 시행 추적**: 튜닝 중 로그에 자동으로 trial ID 주입
- **리소스 관리**: 시행당 CPU/GPU 할당 구성 가능
- **최적 모델 선택**: 튜닝 후 자동으로 최적 모델 체크포인트 선택
- **진행 상황 추적**: 학습/튜닝 단계별 실시간 진행 상황 업데이트

## 모드

### 학습 모드 (기본값)

고정된 하이퍼파라미터를 사용한 표준 모델 학습.

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

### 하이퍼파라미터 튜닝 모드

Ray Tune을 사용한 하이퍼파라미터 최적화.

```json
{
  "action": "train",
  "params": {
    "name": "my_tuning_job",
    "dataset": 123,
    "checkpoint": null,
    "is_tune": true,
    "hyperparameters": [
      {
        "batch_size": { "type": "choice", "values": [16, 32, 64] },
        "learning_rate": { "type": "loguniform", "min": 0.0001, "max": 0.01 },
        "optimizer": { "type": "choice", "values": ["adam", "sgd"] }
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

## 구성 매개변수

### 공통 매개변수 (두 모드 모두)

| 매개변수     | 타입          | 필수 여부 | 설명                               |
| ------------ | ------------- | --------- | ---------------------------------- |
| `name`       | `str`         | 예        | 학습/튜닝 작업 이름                |
| `dataset`    | `int`         | 예        | 데이터셋 ID                        |
| `checkpoint` | `int \| None` | 아니오    | 학습 재개를 위한 체크포인트 ID     |
| `is_tune`    | `bool`        | 아니오    | 튜닝 모드 활성화 (기본값: `false`) |
| `num_cpus`   | `float`       | 아니오    | 시행당 CPU 리소스 (튜닝 전용)      |
| `num_gpus`   | `float`       | 아니오    | 시행당 GPU 리소스 (튜닝 전용)      |

### 학습 모드 매개변수 (`is_tune=false`)

| 매개변수         | 타입   | 필수 여부 | 설명                            |
| ---------------- | ------ | --------- | ------------------------------- |
| `hyperparameter` | `dict` | 예        | 학습을 위한 고정 하이퍼파라미터 |

**참고**: `hyperparameter`의 구조는 완전히 유연하며 플러그인에서 정의합니다. 일반적인 필드는 다음과 같습니다:

- `epochs`: 학습 에폭 수
- `batch_size`: 학습 배치 크기
- `learning_rate`: 학습률
- `optimizer`: 옵티마이저 타입 (adam, sgd 등)
- 플러그인에 필요한 모든 사용자 정의 필드 (예: `dropout_rate`, `weight_decay`, `image_size`)

### 튜닝 모드 매개변수 (`is_tune=true`)

| 매개변수          | 타입   | 필수 여부 | 설명                          |
| ----------------- | ------ | --------- | ----------------------------- |
| `hyperparameters` | `list` | 예        | 하이퍼파라미터 검색 공간 목록 |
| `tune_config`     | `dict` | 예        | Ray Tune 구성                 |

## 하이퍼파라미터 검색 공간

튜닝을 위한 하이퍼파라미터 분포 정의:

### 연속 분포

```python
{
  "learning_rate": {
    "type": "uniform",      # 균등 분포
    "min": 0.0001,
    "max": 0.01
  },
  "dropout_rate": {
    "type": "loguniform",   # 로그 균등 분포
    "min": 0.0001,
    "max": 0.1
  }
}
```

### 이산 분포

```python
{
  "batch_size": {
    "type": "choice",       # 목록에서 선택
    "values": [16, 32, 64, 128]
  },
  "optimizer": {
    "type": "choice",
    "values": ["adam", "sgd", "rmsprop"]
  }
}
```

### 양자화 분포

```python
{
  "learning_rate": {
    "type": "quniform",     # 양자화된 균등 분포
    "min": 0.0001,
    "max": 0.01,
    "q": 0.0001
  }
}
```

### 지원되는 분포 타입

각 하이퍼파라미터 타입은 특정 파라미터가 필요합니다:

| 타입          | 필수 파라미터        | 설명                       | 예시                                                                            |
| ------------- | -------------------- | -------------------------- | ------------------------------------------------------------------------------- |
| `uniform`     | `min`, `max`         | min과 max 사이의 균등 분포 | `{"name": "lr", "type": "uniform", "min": 0.0001, "max": 0.01}`                 |
| `quniform`    | `min`, `max`         | 양자화된 균등 분포         | `{"name": "lr", "type": "quniform", "min": 0.0001, "max": 0.01}`                |
| `loguniform`  | `min`, `max`, `base` | 로그 균등 분포             | `{"name": "lr", "type": "loguniform", "min": 0.0001, "max": 0.01, "base": 10}`  |
| `qloguniform` | `min`, `max`, `base` | 양자화된 로그 균등 분포    | `{"name": "lr", "type": "qloguniform", "min": 0.0001, "max": 0.01, "base": 10}` |
| `randn`       | `mean`, `sd`         | 정규(가우시안) 분포        | `{"name": "noise", "type": "randn", "mean": 0.0, "sd": 1.0}`                    |
| `qrandn`      | `mean`, `sd`         | 양자화된 정규 분포         | `{"name": "noise", "type": "qrandn", "mean": 0.0, "sd": 1.0}`                   |
| `randint`     | `min`, `max`         | min과 max 사이의 랜덤 정수 | `{"name": "epochs", "type": "randint", "min": 5, "max": 15}`                    |
| `qrandint`    | `min`, `max`         | 양자화된 랜덤 정수         | `{"name": "epochs", "type": "qrandint", "min": 5, "max": 15}`                   |
| `lograndint`  | `min`, `max`, `base` | 로그 랜덤 정수             | `{"name": "units", "type": "lograndint", "min": 16, "max": 256, "base": 2}`     |
| `qlograndint` | `min`, `max`, `base` | 양자화된 로그 랜덤 정수    | `{"name": "units", "type": "qlograndint", "min": 16, "max": 256, "base": 2}`    |
| `choice`      | `options`            | 값 목록에서 선택           | `{"name": "optimizer", "type": "choice", "options": ["adam", "sgd"]}`           |
| `grid_search` | `options`            | 모든 값에 대한 그리드 검색 | `{"name": "batch_size", "type": "grid_search", "options": [16, 32, 64]}`        |

**중요 참고사항:**

- 모든 하이퍼파라미터는 `name`과 `type` 필드를 포함해야 합니다
- `loguniform`, `qloguniform`, `lograndint`, `qlograndint`의 경우: `base` 파라미터가 필수입니다 (일반적으로 10 또는 2)
- `choice` 및 `grid_search`의 경우: `options` 사용 (`values` 아님)
- 범위 기반 타입의 경우: `min` 및 `max` 사용 (`lower` 및 `upper` 아님)

## Tune 구성

### 기본 구성

```python
{
  "mode": "max",              # "max" 또는 "min"
  "metric": "accuracy",       # 최적화할 메트릭
  "num_samples": 10,          # 시행 횟수
  "max_concurrent_trials": 2  # 병렬 시행 수
}
```

### 검색 알고리즘 포함

```python
{
  "mode": "max",
  "metric": "accuracy",
  "num_samples": 20,
  "max_concurrent_trials": 4,
  "search_alg": {
    "name": "OptunaSearch",   # 검색 알고리즘
    "points_to_evaluate": [   # 선택적 초기 포인트
      {
        "learning_rate": 0.001,
        "batch_size": 32
      }
    ]
  }
}
```

### 스케줄러 포함

```python
{
  "mode": "max",
  "metric": "accuracy",
  "num_samples": 50,
  "max_concurrent_trials": 8,
  "scheduler": {
    "name": "ASHA",           # 스케줄러 타입
    "options": {
      "grace_period": 10,
      "max_t": 100
    }
  }
}
```

### 지원되는 검색 알고리즘

- `basicvariantgenerator` - 랜덤 검색 (기본값)
- `bayesoptsearch` - 베이지안 최적화
- `hyperoptsearch` - Tree-structured Parzen Estimator

### 지원되는 스케줄러

- `fifo` - First-in-first-out (기본값)
- `hyperband` - HyperBand 스케줄러

## 플러그인 개발

### 학습 모드용

플러그인에서 `train()` 함수 구현:

```python
def train(run, dataset, hyperparameter, checkpoint, **kwargs):
    """
    모델 학습 함수.

    Args:
        run: 로깅을 위한 TrainRun 객체
        dataset: Dataset 객체
        hyperparameter: 하이퍼파라미터가 포함된 dict
        checkpoint: 재개를 위한 선택적 체크포인트
    """
    # 하이퍼파라미터 접근
    epochs = hyperparameter['epochs']
    batch_size = hyperparameter['batch_size']
    learning_rate = hyperparameter['learning_rate']

    # 학습 루프
    for epoch in range(epochs):
        # 한 에폭 학습
        loss, accuracy = train_one_epoch(...)

        # 메트릭 로깅
        run.log_metric('training', 'loss', loss, epoch=epoch)
        run.log_metric('training', 'accuracy', accuracy, epoch=epoch)

        # 시각화 로깅
        run.log_visualization('predictions', 'train', epoch, image_data)

    # 최종 모델 저장
    save_model(model, '/path/to/model.pth')
```

### 튜닝 모드용

플러그인에서 `tune()` 함수 구현:

```python
def tune(hyperparameter, run, dataset, checkpoint, **kwargs):
    """
    하이퍼파라미터 최적화를 위한 튜닝 함수.

    Args:
        hyperparameter: 현재 시행의 하이퍼파라미터가 포함된 dict
        run: 로깅을 위한 TrainRun 객체 (is_tune=True)
        dataset: Dataset 객체
        checkpoint: 재개를 위한 선택적 체크포인트
    """
    from ray import tune

    # 학습 전에 체크포인트 출력 경로 설정
    output_path = Path('/path/to/trial/weights')
    run.checkpoint_output = str(output_path)

    # 학습 루프
    for epoch in range(hyperparameter['epochs']):
        loss, accuracy = train_one_epoch(...)

        # 메트릭 로깅 (trial_id가 자동으로 추가됨)
        run.log_metric('training', 'loss', loss, epoch=epoch)
        run.log_metric('training', 'accuracy', accuracy, epoch=epoch)

    # Ray Tune에 결과 보고
    results = {
        "accuracy": final_accuracy,
        "loss": final_loss
    }

    # 중요: 체크포인트와 함께 보고
    tune.report(
        results,
        checkpoint=tune.Checkpoint.from_directory(run.checkpoint_output)
    )
```

### 매개변수 순서 차이

**중요**: `train()`과 `tune()` 간에 매개변수 순서가 다릅니다:

- `train(run, dataset, hyperparameter, checkpoint, **kwargs)`
- `tune(hyperparameter, run, dataset, checkpoint, **kwargs)`

### 자동 Trial ID 로깅

`is_tune=True`일 때, SDK는 모든 메트릭 및 시각화 로그에 자동으로 `trial_id`를 주입합니다:

```python
# 플러그인 코드
run.log_metric('training', 'loss', 0.5, epoch=10)

# 실제 로깅된 데이터 (trial_id가 자동으로 추가됨)
{
  'category': 'training',
  'key': 'loss',
  'value': 0.5,
  'metrics': {'epoch': 10},
  'trial_id': 'abc123'  # 자동으로 추가됨
}
```

플러그인 변경 불필요 - SDK 레벨에서 투명하게 처리됩니다.

## TuneAction에서 마이그레이션

독립형 `TuneAction`은 이제 **더 이상 사용되지 않습니다**. `is_tune=true`를 사용하는 `TrainAction`으로 마이그레이션하세요:

### 이전 (더 이상 사용되지 않음)

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

### 이후 (권장)

```json
{
  "action": "train",
  "params": {
    "name": "my_tuning_job",
    "dataset": 123,
    "is_tune": true,
    "hyperparameters": [...],
    "tune_config": {...}
  }
}
```

### 주요 변경 사항

1. `"action": "tune"`을 `"action": "train"`으로 변경
2. `"is_tune": true` 추가
3. `"hyperparameter"`를 `"hyperparameters"`로 이름 변경

## 예제

### 간단한 학습

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

### 체크포인트에서 재개

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

### 그리드 검색을 통한 하이퍼파라미터 튜닝

```json
{
  "action": "train",
  "params": {
    "name": "resnet50_tuning",
    "dataset": 456,
    "is_tune": true,
    "hyperparameters": [
      {
        "batch_size": { "type": "grid_search", "values": [16, 32, 64] },
        "learning_rate": { "type": "grid_search", "values": [0.001, 0.0001] },
        "optimizer": { "type": "grid_search", "values": ["adam", "sgd"] }
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

### Optuna 및 ASHA를 사용한 고급 튜닝

```json
{
  "action": "train",
  "params": {
    "name": "resnet50_optuna_tuning",
    "dataset": 456,
    "is_tune": true,
    "num_cpus": 2,
    "num_gpus": 0.5,
    "hyperparameters": [
      {
        "batch_size": { "type": "choice", "values": [16, 32, 64, 128] },
        "learning_rate": { "type": "loguniform", "min": 0.00001, "max": 0.01 },
        "weight_decay": { "type": "loguniform", "min": 0.00001, "max": 0.001 },
        "optimizer": { "type": "choice", "values": ["adam", "sgd", "rmsprop"] }
      }
    ],
    "tune_config": {
      "mode": "max",
      "metric": "validation_accuracy",
      "num_samples": 50,
      "max_concurrent_trials": 8,
      "search_alg": {
        "name": "OptunaSearch"
      },
      "scheduler": {
        "name": "ASHA",
        "options": {
          "grace_period": 10,
          "max_t": 100,
          "reduction_factor": 3
        }
      }
    }
  }
}
```

## 진행 상황 추적

train 액션은 다양한 단계에서 진행 상황을 추적합니다:

### 학습 모드

| 카테고리     | 비율 | 설명          |
| ------------ | ---- | ------------- |
| `validation` | 10%  | 매개변수 검증 |
| `training`   | 90%  | 모델 학습     |

### 튜닝 모드

| 카테고리     | 비율 | 설명                     |
| ------------ | ---- | ------------------------ |
| `validation` | 10%  | 매개변수 검증            |
| `trials`     | 90%  | 하이퍼파라미터 튜닝 시행 |

## 이점

### 통합 인터페이스

- 학습과 튜닝을 위한 단일 액션
- 일관된 매개변수 처리
- 코드 중복 감소

### 유연한 하이퍼파라미터

- SDK에서 고정된 구조 강제하지 않음
- 플러그인이 자체 하이퍼파라미터 스키마 정의
- 검증 오류 없이 사용자 정의 필드 지원

### 고급 HPO

- 다양한 검색 알고리즘 (Optuna, Ax, HyperOpt, BayesOpt)
- 다양한 스케줄러 (ASHA, HyperBand, PBT)
- 자동 최적 모델 선택

### 개발자 경험

- 자동 시행 추적
- 투명한 로깅 향상
- 더 이상 사용되지 않는 TuneAction에서의 명확한 마이그레이션 경로

## 모범 사례

### 하이퍼파라미터 설계

- 합리적인 하이퍼파라미터 검색 공간 유지
- 초기 탐색을 위해 그리드 검색으로 시작
- 효율적인 검색을 위해 베이지안 최적화 (Optuna, Ax) 사용
- 검색 공간 크기에 따라 적절한 `num_samples` 설정

### 리소스 관리

- 시행 리소스 요구 사항에 따라 `num_cpus` 및 `num_gpus` 할당
- 사용 가능한 하드웨어에 따라 `max_concurrent_trials` 설정
- 튜닝 중 리소스 사용량 모니터링

### 체크포인트 관리

- 튜닝 모드에서 학습 전에 항상 `run.checkpoint_output` 설정
- 정기적으로 체크포인트 저장
- 튜닝에서 반환된 최적 체크포인트 사용

### 로깅

- 비교를 위해 모든 관련 메트릭 로깅
- 시행 간에 일관된 메트릭 이름 사용
- 튜닝 보고서에 검증 메트릭 포함

## 문제 해결

### 일반적인 문제

#### "hyperparameter is required when is_tune=False"

학습 모드에서 `hyperparameter`를 제공했는지 확인하세요:

```json
{
  "is_tune": false,
  "hyperparameter": {...}
}
```

#### "hyperparameters is required when is_tune=True"

튜닝 모드에서 `hyperparameters`와 `tune_config`를 제공했는지 확인하세요:

```json
{
  "is_tune": true,
  "hyperparameters": [...],
  "tune_config": {...}
}
```

#### 오류 없이 튜닝 실패

`tune()` 함수가 다음을 수행하는지 확인하세요:

1. 학습 전에 `run.checkpoint_output` 설정
2. 결과 및 체크포인트와 함께 `tune.report()` 호출
3. 예외 없이 적절하게 반환

## 다음 단계

- **플러그인 개발자용**: `train()` 및 선택적으로 `tune()` 함수 구현
- **사용자용**: 학습 모드로 시작한 다음 튜닝 실험
- **고급 사용자용**: 다양한 검색 알고리즘 및 스케줄러 탐색

## 지원 및 리소스

- **API 참조**: TrainAction 클래스 문서 참조
- **예제**: 플러그인 예제 저장소 확인
- **Ray Tune 문서**: https://docs.ray.io/en/latest/tune/
