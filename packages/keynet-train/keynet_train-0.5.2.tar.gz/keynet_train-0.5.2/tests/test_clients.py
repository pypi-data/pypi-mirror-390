"""Tests for BaseMLflowClient with TrainConfig integration."""

import os

import numpy as np
import pytest

from keynet_train.clients.base import BaseMLflowClient


# Test concrete implementation of BaseMLflowClient
class TestMLflowClient(BaseMLflowClient):
    """테스트용 구체 클래스."""

    def upload(self, model):
        """테스트용 더미 upload 메서드."""
        pass

    def _log_tensor(self, model):
        """테스트용 더미 _log_tensor 메서드."""
        pass

    def _log_model(self, model, input_example: np.ndarray) -> str:
        """테스트용 더미 _log_model 메서드."""
        return "test_model_path"


class TestBaseMLflowClientDevelopment:
    """개발 모드 테스트."""

    def test_base_client_development_mode(self):
        """개발 모드에서 BaseMLflowClient 초기화 및 기본값 확인."""
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
        ]
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.pop(var, None)

        try:
            client = TestMLflowClient()

            # 개발 모드 확인
            assert client.is_production is False

            # os.environ에 기본값이 설정되었는지 확인
            assert os.environ["MLFLOW_TRACKING_URI"] == "http://localhost:5000"
            assert os.environ["AWS_ACCESS_KEY_ID"] == "minio"
            assert os.environ["AWS_SECRET_ACCESS_KEY"] == "miniostorage"

            # 모델 메타데이터 기본값 확인
            assert client.model_name == "my_model"
            assert client.train_id == "1"

        finally:
            # 환경변수 복원
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                else:
                    os.environ.pop(var, None)


class TestBaseMLflowClientProduction:
    """프로덕션 모드 테스트."""

    def test_base_client_production_mode_fail(self):
        """프로덕션 모드에서 필수 환경변수 없이 초기화 시 실패."""
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
            # PROFILE만 프로덕션으로 설정
            os.environ["PROFILE"] = "production"

            # 기본값 사용 시 예외 발생
            with pytest.raises(ValueError) as exc_info:
                TestMLflowClient()

            # 예외 메시지에 필수 환경변수들이 포함되어야 함
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
                else:
                    os.environ.pop(var, None)

    def test_base_client_production_mode_success(self):
        """프로덕션 모드에서 모든 환경변수 설정 시 성공."""
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
            client = TestMLflowClient()

            # 프로덕션 모드 확인
            assert client.is_production is True

            # 모델 메타데이터 확인
            assert client.model_name == "production_model"
            assert client.train_id == "prod-train-456"

            # RabbitMQ 설정 확인
            assert client._uploadModelExchange == "prod.model.upload"

            # os.environ에 설정되었는지 확인
            assert os.environ["MLFLOW_TRACKING_URI"] == "http://mlflow.prod.com"
            assert os.environ["AWS_ACCESS_KEY_ID"] == "prod-key-id"
            assert os.environ["RABBIT_ENDPOINT_URL"] == "amqp://rabbit.prod.com"

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


class TestBaseMLflowClientOsEnvOverride:
    """os.environ 우선순위 테스트."""

    def test_respects_existing_env_vars(self):
        """이미 설정된 os.environ 값을 덮어쓰지 않는지 확인."""
        # 사용자가 미리 설정한 값
        os.environ["MLFLOW_TRACKING_URI"] = "http://user-mlflow.com"
        os.environ["AWS_ACCESS_KEY_ID"] = "user-key"

        # PROFILE 제거 (개발 모드)
        original_profile = os.environ.pop("PROFILE", None)

        try:
            client = TestMLflowClient()

            # 기존 값이 유지되어야 함
            assert os.environ["MLFLOW_TRACKING_URI"] == "http://user-mlflow.com"
            assert os.environ["AWS_ACCESS_KEY_ID"] == "user-key"

            # 설정되지 않은 값은 기본값 사용
            assert os.environ["AWS_SECRET_ACCESS_KEY"] == "miniostorage"

        finally:
            # 환경변수 정리
            if original_profile is not None:
                os.environ["PROFILE"] = original_profile
            for var in [
                "MLFLOW_TRACKING_URI",
                "AWS_ACCESS_KEY_ID",
                "AWS_SECRET_ACCESS_KEY",
            ]:
                os.environ.pop(var, None)
