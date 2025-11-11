# keynet-train

MLflow와 통합된 모델 훈련 유틸리티

## 설치

```bash
pip install keynet-train
```

## 주요 기능

### 🚀 자동화된 훈련 API

- 모델에서 자동으로 스키마 추론
- PyTorch 모델을 ONNX로 자동 변환
- MLflow에 자동 로깅 및 버전 관리
- 프레임워크 독립적인 ONNX 모델 로깅 지원

### 📊 지원 프레임워크

#### PyTorch 네이티브 지원

- `@trace_pytorch` 데코레이터로 자동 ONNX 변환 및 배포
- 학습부터 배포까지 완전 자동화

#### 프레임워크 독립적 지원

- `log_onnx_model` 함수로 **모든 프레임워크**의 ONNX 모델 배포
- TensorFlow, JAX, MXNet, PaddlePaddle 등 ONNX 내보내기를 지원하는 모든 프레임워크
- PyTorch 외 프레임워크 사용자를 위한 통합 배포 파이프라인

### 🔧 MLflow 통합

- 실험 자동 생성 및 관리
- 모델 아티팩트 자동 저장 (autolog 기본 활성화)
- 모델 스키마 자동 추론
- 메트릭 및 파라미터 추적 API 제공

## 🚀 기본 사용법

### PyTorch 모델 학습

```python
from keynet_train import trace_pytorch
import torch

# 🎯 decorator에 모델 이름과 샘플 입력을 제공하고, 함수에서는 모델만 반환
@trace_pytorch("my-model", torch.randn(1, 3, 224, 224))
def train_model():
    model = MyModel()

    # 학습 코드...
    for epoch in range(10):
        # 실제 학습 로직
        pass

    return model  # ⚠️ 반드시 torch.nn.Module만 반환
# Experiment 이름: MODEL_ID 있으면 "{MODEL_ID}_my-model", 없으면 "my-model"
```

### 🌐 ONNX 모델 직접 배포

`@trace_pytorch` 데코레이터를 사용할 수 없는 경우, ONNX 파일을 직접 배포할 수 있습니다.

#### PyTorch 수동 변환

```python
from keynet_train import log_onnx_model
import torch

# PyTorch 모델을 수동으로 ONNX 변환
model = MyModel()
model.load_state_dict(torch.load('model.pth'))
dummy_input = torch.randn(1, 3, 224, 224)

torch.onnx.export(model, dummy_input, "model.onnx",
                  input_names=['input'], output_names=['output'])

# 변환된 ONNX 모델 배포
upload_path = log_onnx_model(
    experiment_name="pytorch_manual",
    onnx_model_path="model.onnx",
    metadata={"framework": "pytorch", "conversion": "manual"}
)
```

#### 다른 프레임워크 (TensorFlow, JAX 등)

```python
# 이미 변환된 ONNX 모델 배포
upload_path = log_onnx_model(
    experiment_name="my_experiment",
    onnx_model_path="model.onnx",
    metadata={"framework": "tensorflow", "model_type": "classification"}
)
```

## 📊 MLflow 메트릭 로깅

`@trace_pytorch` 데코레이터는 MLflow 런 관리와 모델 로깅을 자동화하지만, **학습 메트릭은 사용자가 직접 로깅**해야 합니다.

### keynet-train 자동화 범위

#### ✅ 자동으로 처리되는 것

- MLflow 실험/런 생성 및 관리
- 모델 스키마 자동 추론 (실제 모델 실행)
- 모델 아티팩트 자동 로깅 (`enable_autolog=True` 기본값)
- PyTorch → ONNX 자동 변환
- S3/MinIO 자동 업로드
- RabbitMQ 메시지 발행
- Triton config.pbtxt 생성

#### 📝 사용자가 직접 처리하는 것

- **학습 메트릭 로깅** (`mlflow.log_metric()`)
- **하이퍼파라미터 로깅** (`mlflow.log_params()`)
- **커스텀 아티팩트/태그** (`mlflow.log_artifact()`, `mlflow.set_tag()`)

### 메트릭 로깅 패턴

```python
import mlflow
from keynet_train import trace_pytorch
import torch

@trace_pytorch("mnist-classifier", torch.randn(1, 28, 28))
def train_mnist():
    model = MNISTModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 하이퍼파라미터 로깅
    mlflow.log_params({
        "learning_rate": 0.001,
        "batch_size": 32,
        "optimizer": "Adam",
        "epochs": 10
    })

    for epoch in range(10):
        train_loss, train_acc = train_one_epoch(model, optimizer, train_loader)

        # 메트릭 로깅 (step 단위)
        mlflow.log_metrics({
            "train_loss": train_loss,
            "train_accuracy": train_acc
        }, step=epoch)

    # 최종 메트릭
    mlflow.log_metric("final_accuracy", train_acc)

    return model  # 모델은 autolog에 의해 자동 저장됨
```

### MLflow Autolog 제어

기본적으로 `enable_autolog=True`로 설정되어 모델이 자동 로깅됩니다. 필요 시 비활성화할 수 있습니다:

```python
# Autolog 비활성화 (모델도 수동 로깅 필요)
@trace_pytorch(
    "custom-model",
    torch.randn(1, 784),
    enable_autolog=False  # 모델 자동 로깅 비활성화
)
def train_with_manual_logging():
    model = MyModel()
    # 학습...

    # enable_autolog=False일 때도 메트릭은 직접 로깅
    mlflow.log_metric("accuracy", 0.95)

    return model
```

## 🔧 환경 설정

로컬 개발 환경에서는 별도 설정 없이 바로 사용 가능합니다. 프로덕션 환경에서는 다음 환경변수를 설정하세요:

```bash
# 필수 환경변수
export MLFLOW_TRACKING_URI="http://mlflow.production.com"
export MLFLOW_S3_ENDPOINT_URL="http://minio.production.com:9000"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

환경변수 설정 후 코드 변경 없이 동일하게 사용하면 됩니다.

## 📋 반환값 제약사항

**`@trace_pytorch` 데코레이터를 사용하는 함수는 반드시 `torch.nn.Module` 객체만 반환해야 합니다.**

### ✅ 올바른 사용법

```python
@trace_pytorch("mnist-v1", torch.randn(1, 784))
def train_mnist():
    model = torch.nn.Sequential(
        torch.nn.Linear(784, 128),
        torch.nn.ReLU(),
        torch.nn.Linear(128, 10)
    )

    # 훈련 로직
    optimizer = torch.optim.Adam(model.parameters())
    for epoch in range(100):
        # 실제 훈련...
        loss = train_one_epoch(model, optimizer, train_loader)

        # 메트릭은 mlflow.log_* 함수로 기록
        mlflow.log_metric("train_loss", loss, step=epoch)

    return model  # 🎯 모델만 반환!
```

### ❌ 잘못된 사용법들

```python
@trace_pytorch("wrong-model-1", torch.randn(1, 784))
def wrong_usage1():
    model = MyModel()
    loss = train(model)
    return model, loss  # ❌ 튜플 반환 불가

@trace_pytorch("wrong-model-2", torch.randn(1, 784))
def wrong_usage2():
    model = MyModel()
    train(model)
    return {
        "model": model,
        "accuracy": 0.95
    }  # ❌ 딕셔너리 반환 불가

@trace_pytorch("wrong-model-3", torch.randn(1, 784))
def wrong_usage3():
    model = MyModel()
    train(model)
    return "model_saved.pth"  # ❌ 문자열 반환 불가
```

### 💡 왜 이런 제약이 있나요?

`@trace_pytorch` 데코레이터는 내부적으로 다음 작업을 자동화합니다:

1. **MLflow 모델 로깅**: `mlflow.pytorch.log_model(pytorch_model=model, ...)`
2. **ONNX 변환**: `torch.onnx.export(model, ...)`
3. **Triton 배포**: 자동 `config.pbtxt` 생성

이 모든 작업이 `torch.nn.Module` 객체를 필요로 하므로, 다른 타입의 반환값은 지원하지 않습니다.

## 📝 ONNX 모델 입출력 파라미터명 규칙

`@trace_pytorch` 데코레이터를 사용할 때 생성되는 ONNX 모델의 입출력 파라미터명은 다음과 같이 결정됩니다:

### 입력 파라미터 (Inputs)

```python
# ✅ Dictionary 형태로 입력하면 키 이름을 사용 (권장)
@trace_pytorch(
    "multi-input-model",
    {"image": torch.randn(1, 3, 224, 224), "label": torch.randn(1, 10)}
)
def train_model():
    # 생성되는 ONNX의 입력명: "image", "label"
    ...

# ✅ 단일 텐서로 입력하면 자동 생성
@trace_pytorch("simple-model", torch.randn(1, 3, 224, 224))
def train_model():
    # 생성되는 ONNX의 입력명: "input_0"
    ...
```

### 출력 파라미터 (Outputs)

```python
# 출력명은 항상 자동 생성됩니다
@trace_pytorch("output-test", torch.randn(1, 3, 224, 224))
def train_model():
    # 단일 출력: "output_0"
    return model

# 다중 출력 모델의 경우
def train_multi_output_model():
    class MultiOutputModel(torch.nn.Module):
        def forward(self, x):
            return output1, output2  # 튜플 반환

    # 실제로는 MLflow가 튜플을 하나의 배열로 처리하여 "output_0"만 생성됨
    return model
```

### ⚠️ 중요한 제한사항

- **지원되는 입력 형태**: `torch.Tensor` 또는 `Dict[str, torch.Tensor]`만 지원
- **튜플 입력 미지원**: `(tensor1, tensor2)` 형태의 튜플 입력은 현재 지원되지 않음
- **다중 출력 처리**: PyTorch 모델이 튜플로 다중 출력을 반환해도 MLflow signature 추론에 의해 `output_0` 하나로 처리됨
- **MLflow 의존성**: 파라미터명 생성은 MLflow의 자동 signature 추론에 의존하므로 일부 제한사항이 있음

### 💡 권장사항

```python
# 🎯 최적의 사용법: Dictionary 입력으로 명시적인 이름 지정
@trace_pytorch(
    "segmentation-model",
    {
        "image": torch.randn(1, 3, 224, 224),
        "mask": torch.randn(1, 1, 224, 224)
    }
)
def train_model():
    # 생성되는 config.pbtxt에서 명확한 입력명 확인 가능:
    # input { name: "image", data_type: TYPE_FP32, dims: [-1, 3, 224, 224] }
    # input { name: "mask", data_type: TYPE_FP32, dims: [-1, 1, 224, 224] }
    return model
```

> **Note:** 생성된 ONNX 모델은 Triton Inference Server 배포 시 자동으로 `config.pbtxt` 파일이 생성되어 정확한 입출력 스키마를 확인할 수 있습니다.

### 다중 입력 모델

```python
@trace_pytorch(
    "multi-input-v1",
    {
        "image": torch.randn(1, 3, 224, 224),
        "mask": torch.randn(1, 1, 224, 224)
    }
)
def train_multi_input():
    model = MultiInputModel()

    # 모델이 여러 입력을 받는 경우
    class MultiInputModel(torch.nn.Module):
        def forward(self, image, mask):
            # image와 mask를 함께 처리
            combined = torch.cat([image, mask], dim=1)
            return self.classifier(combined)

    # 훈련 로직...
    return model
```

## 🔄 Dynamic Axes (가변 크기 지원)

ONNX 변환 시 입출력 텐서의 특정 차원을 동적(가변) 크기로 설정할 수 있습니다.

### 기본 동작

```python
# 기본적으로 배치 차원(0번)은 자동으로 동적 크기로 설정됩니다
@trace_pytorch("dynamic-batch-model", torch.randn(1, 3, 224, 224))
def train_model():
    # ONNX 입력 shape: [-1, 3, 224, 224]
    # -1은 가변 배치 크기를 의미
    return model
```

### 커스텀 Dynamic Axes

```python
# 시퀀스 길이가 가변적인 모델
@trace_pytorch(
    "sequence-model",
    torch.randn(1, 128, 768),  # [batch, seq_len, hidden]
    dynamic_axes={
        "input_0": {
            0: "batch_size",
            1: "sequence_length"  # 1번 차원도 가변으로
        },
        "output_0": {
            0: "batch_size",
            1: "sequence_length"
        }
    }
)
def train_sequence_model():
    return SequenceModel()

# 다중 입력에서 각각 다른 dynamic axes 설정
@trace_pytorch(
    "multimodal-model",
    {
        "image": torch.randn(1, 3, 224, 224),
        "text": torch.randn(1, 50, 512)
    },
    dynamic_axes={
        "image": {0: "batch"},           # 이미지는 배치만
        "text": {0: "batch", 1: "len"}, # 텍스트는 길이도
        "output_0": {0: "batch"}
    }
)
def train_multimodal():
    return MultiModalModel()
```

### 사용 시나리오

- **NLP**: 가변 길이 시퀀스 처리
- **Vision**: 다양한 해상도 이미지 지원
- **Detection**: 가변 개수의 객체 출력

> **Note**: 동적 크기 설정이 실패하면 자동으로 고정 크기로 변환됩니다.
