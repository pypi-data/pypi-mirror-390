"""End-to-end integration tests for keynet-train."""

import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import mlflow
import pytest
import torch
import torch.nn as nn

from keynet_train import TrainConfig, log_onnx_model, trace_pytorch


class SimpleMNISTModel(nn.Module):
    """Simple MNIST-like model for E2E testing."""

    def __init__(self):
        """Initialize the model."""
        super().__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(784, 128)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        """Forward pass."""
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


@pytest.fixture
def setup_mlflow():
    """Setup MLflow for E2E testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mlflow.set_tracking_uri(f"file://{tmpdir}")
        yield tmpdir


@pytest.fixture
def unique_experiment_name():
    """Generate unique experiment name for test isolation."""
    return f"e2e_test_{uuid.uuid4().hex[:8]}"


class TestE2ETrainingFlow:
    """End-to-end training flow tests."""

    def test_e2e_training_flow(self, setup_mlflow, unique_experiment_name):
        """
        Test complete training flow with TrainConfig and @trace_pytorch.

        이 테스트는 다음을 검증합니다:
        1. TrainConfig 생성 및 기본값 확인
        2. @trace_pytorch 데코레이터 사용
        3. mlflow.log_metric 호출
        4. 모델 반환 확인
        5. MLflow 실험 생성 확인
        """
        # 1. TrainConfig 생성 및 기본값 확인
        config = TrainConfig()
        assert config is not None
        assert hasattr(config, "mlflow_tracking_uri")
        assert hasattr(config, "is_production")
        assert config.is_production is False  # 기본값은 development

        # 2. @trace_pytorch 데코레이터 사용
        with patch("keynet_train.decorators.pytorch.onnx_client") as mock_client:
            mock_client.upload.return_value = "mocked/path"

            @trace_pytorch(
                "mnist-e2e-model",
                torch.randn(1, 28, 28),
                run_name="e2e_test_run",
                auto_convert_onnx=True,
                enable_autolog=False,
            )
            def train_mnist_model():
                model = SimpleMNISTModel()

                # 3. mlflow.log_metric 호출
                mlflow.log_metric("train_loss", 0.5, step=0)
                mlflow.log_metric("train_loss", 0.3, step=1)
                mlflow.log_metric("train_loss", 0.1, step=2)

                mlflow.log_metric("train_accuracy", 0.8, step=0)
                mlflow.log_metric("train_accuracy", 0.9, step=1)
                mlflow.log_metric("train_accuracy", 0.95, step=2)

                # 훈련 파라미터 로깅
                mlflow.log_params(
                    {
                        "learning_rate": 0.001,
                        "batch_size": 32,
                        "epochs": 3,
                        "optimizer": "Adam",
                    }
                )

                # 4. 모델 반환 확인
                return model

            # 데코레이터 실행
            trained_model = train_mnist_model()

            # 모델이 올바르게 반환되었는지 확인
            assert trained_model is not None
            assert isinstance(trained_model, SimpleMNISTModel)
            assert isinstance(trained_model, nn.Module)

            # 5. MLflow 실험 생성 확인
            experiment = mlflow.get_experiment_by_name("mnist-e2e-model")
            assert experiment is not None

            # Run이 생성되었는지 확인
            runs = mlflow.search_runs(
                experiment_names=["mnist-e2e-model"],
                filter_string="tags.mlflow.runName = 'e2e_test_run'",
            )
            assert len(runs) == 1

            # 메트릭이 로깅되었는지 확인 (최종 값 검증)
            run = runs.iloc[0]
            assert "metrics.train_loss" in run
            assert "metrics.train_accuracy" in run
            # 최종 step의 메트릭 값 검증
            assert run["metrics.train_loss"] == 0.1
            assert run["metrics.train_accuracy"] == 0.95

            # 파라미터가 로깅되었는지 확인
            assert run["params.learning_rate"] == "0.001"
            assert run["params.batch_size"] == "32"
            assert run["params.epochs"] == "3"

            # ONNX 업로드가 호출되었는지 확인
            assert mock_client.upload.called

    def test_e2e_framework_agnostic_workflow(
        self, setup_mlflow, unique_experiment_name
    ):
        """
        Test framework-agnostic ONNX deployment workflow.

        이 테스트는 다음을 검증합니다:
        1. 임의의 프레임워크에서 ONNX 모델 생성
        2. log_onnx_model 함수로 MLflow에 로깅
        3. 메타데이터 포함 확인
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. ONNX 모델 생성 (실제로는 TensorFlow/JAX 등에서 변환됨)
            onnx_path = Path(tmpdir) / "framework_agnostic.onnx"

            # 간단한 PyTorch 모델을 ONNX로 변환 (프레임워크 독립적 시뮬레이션)
            model = nn.Linear(10, 5)
            dummy_input = torch.randn(1, 10)
            torch.onnx.export(
                model,
                dummy_input,
                str(onnx_path),
                input_names=["input"],
                output_names=["output"],
            )

            # 2. log_onnx_model로 MLflow에 로깅
            with patch("keynet_train.decorators.onnx.onnx_client") as mock_client:
                mock_client.upload.return_value = "mocked/onnx/path"

                result = log_onnx_model(
                    experiment_name=unique_experiment_name,
                    onnx_model_path=onnx_path,
                    run_name="tensorflow_model",
                    model_name="linear_classifier",
                    metadata={
                        "framework": "tensorflow",
                        "version": "2.13.0",
                        "model_type": "classification",
                        "input_shape": [None, 10],
                        "output_shape": [None, 5],
                    },
                )

                # 업로드가 성공했는지 확인
                assert result == "mocked/onnx/path"
                assert mock_client.upload.called

                # 3. 메타데이터 포함 확인
                experiment = mlflow.get_experiment_by_name(unique_experiment_name)
                assert experiment is not None

                runs = mlflow.search_runs(
                    experiment_names=[unique_experiment_name],
                    filter_string="tags.mlflow.runName = 'tensorflow_model'",
                )
                assert len(runs) == 1

                run = runs.iloc[0]
                assert run["params.framework"] == "tensorflow"
                assert run["params.version"] == "2.13.0"
                assert run["params.model_type"] == "classification"

    def test_e2e_multi_input_model(self, setup_mlflow, unique_experiment_name):
        """
        Test E2E flow with multi-input model.

        이 테스트는 다음을 검증합니다:
        1. 다중 입력 모델 정의
        2. Dict[str, Tensor] 형식의 sample_input 사용
        3. dynamic_axes 설정
        """

        class MultiInputModel(nn.Module):
            """Multi-input model for testing."""

            def __init__(self):
                """Initialize multi-input model."""
                super().__init__()
                self.text_encoder = nn.Linear(100, 64)
                self.image_encoder = nn.Linear(784, 64)
                self.combiner = nn.Linear(128, 10)

            def forward(self, text, image):
                """Forward pass with multiple inputs."""
                text_features = self.text_encoder(text)
                image_features = self.image_encoder(image)
                combined = torch.cat([text_features, image_features], dim=1)
                return self.combiner(combined)

        # Dict 형식의 sample_input 정의
        sample_inputs = {
            "text": torch.randn(1, 100),
            "image": torch.randn(1, 784),
        }

        # dynamic_axes 설정
        dynamic_axes = {
            "text": {0: "batch_size"},
            "image": {0: "batch_size"},
            "output": {0: "batch_size"},
        }

        with patch("keynet_train.decorators.pytorch.onnx_client") as mock_client:
            mock_client.upload.return_value = "mocked/multi/path"

            @trace_pytorch(
                "multi-input-e2e-model",
                sample_inputs,
                dynamic_axes=dynamic_axes,
                auto_convert_onnx=True,
                enable_autolog=False,
            )
            def train_multi_input():
                model = MultiInputModel()
                mlflow.log_metric("combined_loss", 0.3)
                return model

            model = train_multi_input()

            assert isinstance(model, MultiInputModel)
            assert mock_client.upload.called

            # 실험 확인
            experiment = mlflow.get_experiment_by_name("multi-input-e2e-model")
            assert experiment is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
