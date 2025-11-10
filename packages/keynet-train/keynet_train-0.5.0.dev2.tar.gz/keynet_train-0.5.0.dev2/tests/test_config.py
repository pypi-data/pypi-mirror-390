"""Tests for TrainConfig."""

import os

import pytest

from keynet_train.config import TrainConfig


class TestTrainConfigDefaults:
    """기본값 테스트."""

    def test_defaults_without_env_vars(self):
        """환경변수 없이 기본값 사용."""
        # 환경변수 초기화 (테스트 격리)
        env_vars = [
            "PROFILE",
            "MLFLOW_TRACKING_URI",
            "MLFLOW_S3_ENDPOINT_URL",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "MODEL_NAME",
            "TRAIN_ID",
            "RABBIT_ENDPOINT_URL",
            "RABBIT_MODEL_UPLOAD_TOPIC",
            "DATASET_PATH",
        ]
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.pop(var, None)

        try:
            config = TrainConfig()

            # 환경 프로필 기본값 검증
            assert config.profile is None

            # MLflow 기본값 검증
            assert config.mlflow_tracking_uri == "http://localhost:5000"
            assert config.mlflow_s3_endpoint_url is None

            # S3 기본값 검증
            assert config.aws_access_key_id.get_secret_value() == "minio"
            assert config.aws_secret_access_key.get_secret_value() == "miniostorage"

            # 모델 메타데이터 기본값 검증
            assert config.model_name == "my_model"
            assert config.train_id == "1"

            # RabbitMQ 기본값 검증
            assert config.rabbit_endpoint_url is None
            assert config.rabbit_model_upload_topic is None

            # 데이터셋 경로 기본값 검증
            assert config.dataset_path == "/data"

        finally:
            # 환경변수 복원
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value


class TestTrainConfigEnvVars:
    """환경변수 로딩 테스트."""

    def test_loads_from_env_vars(self):
        """환경변수에서 값 로딩."""
        # 환경변수 설정
        os.environ["PROFILE"] = "prod"
        os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow.example.com"
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio.example.com:9000"
        os.environ["AWS_ACCESS_KEY_ID"] = "test-key-id"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret-key"
        os.environ["MODEL_NAME"] = "test_model"
        os.environ["TRAIN_ID"] = "test-123"
        os.environ["RABBIT_ENDPOINT_URL"] = "amqp://rabbit.example.com"
        os.environ["RABBIT_MODEL_UPLOAD_TOPIC"] = "test.model.upload"
        os.environ["DATASET_PATH"] = "/mnt/datasets"

        try:
            config = TrainConfig()

            # 환경변수 값 검증
            assert config.profile == "prod"
            assert config.mlflow_tracking_uri == "http://mlflow.example.com"
            assert config.mlflow_s3_endpoint_url == "http://minio.example.com:9000"
            assert config.aws_access_key_id.get_secret_value() == "test-key-id"
            assert config.aws_secret_access_key.get_secret_value() == "test-secret-key"
            assert config.model_name == "test_model"
            assert config.train_id == "test-123"
            assert config.rabbit_endpoint_url == "amqp://rabbit.example.com"
            assert config.rabbit_model_upload_topic == "test.model.upload"
            assert config.dataset_path == "/mnt/datasets"

        finally:
            # 환경변수 정리
            del os.environ["PROFILE"]
            del os.environ["MLFLOW_TRACKING_URI"]
            del os.environ["MLFLOW_S3_ENDPOINT_URL"]
            del os.environ["AWS_ACCESS_KEY_ID"]
            del os.environ["AWS_SECRET_ACCESS_KEY"]
            del os.environ["MODEL_NAME"]
            del os.environ["TRAIN_ID"]
            del os.environ["RABBIT_ENDPOINT_URL"]
            del os.environ["RABBIT_MODEL_UPLOAD_TOPIC"]
            del os.environ["DATASET_PATH"]


class TestTrainConfigSecretStr:
    """SecretStr 자동 마스킹 테스트."""

    def test_secret_str_masking(self):
        """SecretStr 필드가 자동으로 마스킹되는지 확인."""
        config = TrainConfig()

        # SecretStr은 str()로 출력 시 마스킹됨
        assert "**********" in str(config.aws_access_key_id)
        assert "minio" not in str(config.aws_access_key_id)

        assert "**********" in str(config.aws_secret_access_key)
        assert "miniostorage" not in str(config.aws_secret_access_key)

        # repr()로도 마스킹됨
        assert "**********" in repr(config.aws_access_key_id)
        assert "**********" in repr(config.aws_secret_access_key)

        # get_secret_value()로만 실제 값 접근 가능
        assert config.aws_access_key_id.get_secret_value() == "minio"
        assert config.aws_secret_access_key.get_secret_value() == "miniostorage"


class TestTrainConfigProductionCheck:
    """Production 환경 검증 테스트."""

    def test_check_production_vars_fails_with_defaults(self):
        """기본값 사용 시 check_production_vars() 예외 발생."""
        # 환경변수 초기화
        env_vars = [
            "PROFILE",
            "MLFLOW_TRACKING_URI",
            "MLFLOW_S3_ENDPOINT_URL",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "MODEL_NAME",
            "TRAIN_ID",
            "RABBIT_ENDPOINT_URL",
            "RABBIT_MODEL_UPLOAD_TOPIC",
        ]
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.pop(var, None)

        try:
            config = TrainConfig()

            # 기본값 사용 시 예외 발생
            with pytest.raises(ValueError) as exc_info:
                config.check_production_vars()

            # 예외 메시지에 모든 기본값 환경변수가 포함되어야 함
            error_message = str(exc_info.value)
            assert "MLFLOW_TRACKING_URI" in error_message
            assert "MLFLOW_S3_ENDPOINT_URL" in error_message
            assert "AWS_ACCESS_KEY_ID" in error_message
            assert "AWS_SECRET_ACCESS_KEY" in error_message
            assert "MODEL_NAME" in error_message
            assert "TRAIN_ID" in error_message
            assert "RABBIT_ENDPOINT_URL" in error_message
            assert "RABBIT_MODEL_UPLOAD_TOPIC" in error_message

        finally:
            # 환경변수 복원
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value

    def test_check_production_vars_passes_with_real_values(self):
        """실제 환경변수 설정 시 check_production_vars() 통과."""
        # Production 환경변수 설정
        os.environ["PROFILE"] = "production"
        os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow.prod.com"
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio.prod.com:9000"
        os.environ["AWS_ACCESS_KEY_ID"] = "prod-key-id"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "prod-secret-key"
        os.environ["MODEL_NAME"] = "production_model"
        os.environ["TRAIN_ID"] = "prod-train-456"
        os.environ["RABBIT_ENDPOINT_URL"] = "amqp://rabbit.prod.com"
        os.environ["RABBIT_MODEL_UPLOAD_TOPIC"] = "prod.model.upload"

        try:
            config = TrainConfig()

            # 실제 값 사용 시 예외 없이 통과
            config.check_production_vars()  # 예외 발생 안 함 ✅

        finally:
            # 환경변수 정리
            del os.environ["PROFILE"]
            del os.environ["MLFLOW_TRACKING_URI"]
            del os.environ["MLFLOW_S3_ENDPOINT_URL"]
            del os.environ["AWS_ACCESS_KEY_ID"]
            del os.environ["AWS_SECRET_ACCESS_KEY"]
            del os.environ["MODEL_NAME"]
            del os.environ["TRAIN_ID"]
            del os.environ["RABBIT_ENDPOINT_URL"]
            del os.environ["RABBIT_MODEL_UPLOAD_TOPIC"]

    def test_check_production_vars_partial_defaults(self):
        """일부만 기본값일 때 해당 필드만 에러 메시지에 포함."""
        # 일부만 실제 값 설정
        os.environ["PROFILE"] = "dev"  # production이 아니므로 PROFILE은 기본값과 다름
        os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow.prod.com"
        os.environ["AWS_ACCESS_KEY_ID"] = "prod-key-id"
        os.environ["MODEL_NAME"] = "production_model"
        # 나머지는 기본값 사용

        original_values = {}
        for var in [
            "MLFLOW_S3_ENDPOINT_URL",
            "AWS_SECRET_ACCESS_KEY",
            "TRAIN_ID",
            "RABBIT_ENDPOINT_URL",
            "RABBIT_MODEL_UPLOAD_TOPIC",
        ]:
            original_values[var] = os.environ.pop(var, None)

        try:
            config = TrainConfig()

            with pytest.raises(ValueError) as exc_info:
                config.check_production_vars()

            error_message = str(exc_info.value)

            # 설정한 값들은 에러 메시지에 없음
            assert "MLFLOW_TRACKING_URI" not in error_message

            # 기본값인 것들만 에러 메시지에 포함
            assert "MLFLOW_S3_ENDPOINT_URL" in error_message
            assert "AWS_SECRET_ACCESS_KEY" in error_message
            assert "TRAIN_ID" in error_message
            assert "RABBIT_ENDPOINT_URL" in error_message
            assert "RABBIT_MODEL_UPLOAD_TOPIC" in error_message

        finally:
            # 환경변수 정리
            del os.environ["PROFILE"]
            del os.environ["MLFLOW_TRACKING_URI"]
            del os.environ["AWS_ACCESS_KEY_ID"]
            del os.environ["MODEL_NAME"]
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value


class TestTrainConfigProfile:
    """PROFILE 환경변수 및 is_production 프로퍼티 테스트."""

    def test_profile_default(self):
        """PROFILE 기본값은 None."""
        # 환경변수 초기화
        original_profile = os.environ.pop("PROFILE", None)

        try:
            config = TrainConfig()
            assert config.profile is None

        finally:
            if original_profile is not None:
                os.environ["PROFILE"] = original_profile

    def test_profile_from_env(self):
        """환경변수에서 PROFILE 로딩."""
        os.environ["PROFILE"] = "prod"

        try:
            config = TrainConfig()
            assert config.profile == "prod"

        finally:
            del os.environ["PROFILE"]

    def test_is_production_false_by_default(self):
        """PROFILE 미설정 시 is_production은 False."""
        original_profile = os.environ.pop("PROFILE", None)

        try:
            config = TrainConfig()
            assert config.is_production is False

        finally:
            if original_profile is not None:
                os.environ["PROFILE"] = original_profile

    def test_is_production_false_for_dev(self):
        """PROFILE이 'dev' 등 다른 값이면 is_production은 False."""
        os.environ["PROFILE"] = "dev"

        try:
            config = TrainConfig()
            assert config.is_production is False

        finally:
            del os.environ["PROFILE"]

    def test_is_production_true_for_prod(self):
        """PROFILE이 'prod'이면 is_production은 True."""
        os.environ["PROFILE"] = "prod"

        try:
            config = TrainConfig()
            assert config.is_production is True

        finally:
            del os.environ["PROFILE"]

    def test_is_production_true_for_production(self):
        """PROFILE이 'production'이면 is_production은 True."""
        os.environ["PROFILE"] = "production"

        try:
            config = TrainConfig()
            assert config.is_production is True

        finally:
            del os.environ["PROFILE"]
