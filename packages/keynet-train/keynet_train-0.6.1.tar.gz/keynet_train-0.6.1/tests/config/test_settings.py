"""MODEL_ID 지원을 포함한 TrainConfig 테스트."""

import os
from unittest.mock import patch

from keynet_train.config.settings import TrainConfig


class TestTrainConfigModelId:
    """MODEL_ID 환경변수 처리 테스트."""

    def test_model_id_default_none(self):
        """MODEL_ID가 설정되지 않았을 때 None으로 기본값 설정되는지 테스트."""
        config = TrainConfig()
        assert config.model_id is None

    def test_model_id_from_environment(self):
        """환경변수에서 MODEL_ID가 로드되는지 테스트."""
        with patch.dict(os.environ, {"MODEL_ID": "42"}):
            config = TrainConfig()
            assert config.model_id == "42"

    def test_model_id_case_insensitive(self):
        """MODEL_ID가 대소문자를 구분하지 않는지 테스트."""
        with patch.dict(os.environ, {"model_id": "123"}):
            config = TrainConfig()
            assert config.model_id == "123"

    def test_model_id_with_hyphen(self):
        """하이픈이 포함된 형식의 MODEL_ID 테스트."""
        with patch.dict(os.environ, {"MODEL_ID": "project-42-v2"}):
            config = TrainConfig()
            assert config.model_id == "project-42-v2"

    def test_production_mode_without_model_id(self):
        """프로덕션 모드에서 MODEL_ID가 필수가 아님을 테스트 (선택사항)."""
        with patch.dict(
            os.environ,
            {
                "PROFILE": "prod",
                "MLFLOW_TRACKING_URI": "http://mlflow.prod.com",
                "MLFLOW_S3_ENDPOINT_URL": "http://s3.prod.com",
                "AWS_ACCESS_KEY_ID": "prod-key",
                "AWS_SECRET_ACCESS_KEY": "prod-secret",
                "MODEL_NAME": "prod-model",
                "TRAIN_ID": "prod-123",
                "RABBIT_ENDPOINT_URL": "amqp://rabbit.prod.com",
                "RABBIT_MODEL_UPLOAD_TOPIC": "model.upload",
            },
        ):
            config = TrainConfig()
            config.check_production_vars()  # MODEL_ID 없이도 통과해야 함
