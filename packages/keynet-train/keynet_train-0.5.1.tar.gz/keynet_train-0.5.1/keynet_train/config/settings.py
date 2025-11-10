"""TrainConfig: Pydantic 기반 환경변수 관리 클래스."""

from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class TrainConfig(BaseSettings):
    """
    MLflow, S3, RabbitMQ 환경변수를 관리하는 Pydantic 기반 설정 클래스.

    환경변수에서 자동으로 값을 로드하며, 로컬 개발을 위한 기본값을 제공합니다.
    민감정보(SecretStr)는 로그/출력 시 자동으로 마스킹됩니다.

    환경변수 목록:
        개발 환경 (기본값 사용 가능):
            - MLFLOW_TRACKING_URI: MLflow 서버 URI (기본: http://localhost:5000)
            - MODEL_NAME: 모델 이름 (기본: my_model)
            - TRAIN_ID: 훈련 ID (기본: 1)
            - AWS_ACCESS_KEY_ID: S3/MinIO 액세스 키 (기본: minio)
            - AWS_SECRET_ACCESS_KEY: S3/MinIO 시크릿 키 (기본: miniostorage)
            - DATASET_PATH: 데이터셋 기본 경로 (기본: /data)

        프로덕션 환경 (PROFILE=prod 설정 시 모든 값 필수):
            - PROFILE: 환경 프로필 (prod 또는 production)
            - MLFLOW_TRACKING_URI: 실제 MLflow 서버 URI
            - MLFLOW_S3_ENDPOINT_URL: S3/MinIO 엔드포인트 URL
            - AWS_ACCESS_KEY_ID: 실제 S3/MinIO 액세스 키
            - AWS_SECRET_ACCESS_KEY: 실제 S3/MinIO 시크릿 키
            - MODEL_NAME: 실제 모델 이름
            - TRAIN_ID: 실제 훈련 ID
            - RABBIT_ENDPOINT_URL: RabbitMQ 엔드포인트 URL
            - RABBIT_MODEL_UPLOAD_TOPIC: RabbitMQ 토픽

    Attributes:
        profile: 환경 프로필 (None, "prod", "production")
        mlflow_tracking_uri: MLflow 서버 URI
        mlflow_s3_endpoint_url: S3/MinIO 엔드포인트 URL
        aws_access_key_id: S3/MinIO 액세스 키 (SecretStr)
        aws_secret_access_key: S3/MinIO 시크릿 키 (SecretStr)
        model_name: 모델 이름
        train_id: 훈련 ID
        rabbit_endpoint_url: RabbitMQ 엔드포인트 URL
        rabbit_model_upload_topic: RabbitMQ 토픽
        dataset_path: 데이터셋 기본 경로
        is_production: Production 환경 여부 확인 (property)

    Examples:
        기본 사용법 (개발 환경):
            >>> config = TrainConfig()
            >>> config.mlflow_tracking_uri
            'http://localhost:5000'
            >>> config.is_production
            False

        환경변수 설정:
            >>> import os
            >>> os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow.example.com"
            >>> config = TrainConfig()
            >>> config.mlflow_tracking_uri
            'http://mlflow.example.com'

        프로덕션 환경 검증:
            >>> os.environ["PROFILE"] = "prod"
            >>> config = TrainConfig()
            >>> config.is_production
            True
            >>> config.check_production_vars()  # 기본값이면 ValueError 발생

    Note:
        - 개발 환경에서는 기본값으로 작동하므로 환경변수 설정 불필요
        - 프로덕션 환경에서는 check_production_vars()로 검증 필수
        - SecretStr 타입은 get_secret_value()로 실제 값 접근

    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    # 환경 프로필
    profile: Optional[str] = Field(
        default=None,
        validation_alias="PROFILE",
        description="Environment profile (prod/production for production mode)",
    )

    # MLflow 설정
    mlflow_tracking_uri: str = Field(
        default="http://localhost:5000",
        validation_alias="MLFLOW_TRACKING_URI",
        description="MLflow tracking server URI",
    )

    mlflow_s3_endpoint_url: Optional[str] = Field(
        default=None,
        validation_alias="MLFLOW_S3_ENDPOINT_URL",
        description="S3/MinIO endpoint URL (None for AWS S3)",
    )

    # S3 자격증명
    aws_access_key_id: SecretStr = Field(
        default=SecretStr("minio"),
        validation_alias="AWS_ACCESS_KEY_ID",
        description="AWS/MinIO access key ID",
    )

    aws_secret_access_key: SecretStr = Field(
        default=SecretStr("miniostorage"),
        validation_alias="AWS_SECRET_ACCESS_KEY",
        description="AWS/MinIO secret access key",
    )

    # 모델 메타데이터
    model_name: str = Field(
        default="my_model",
        validation_alias="MODEL_NAME",
        description="Model name",
    )

    train_id: str = Field(
        default="1",
        validation_alias="TRAIN_ID",
        description="Training ID",
    )

    # RabbitMQ 설정 (Production 전용)
    rabbit_endpoint_url: Optional[str] = Field(
        default=None,
        validation_alias="RABBIT_ENDPOINT_URL",
        description="RabbitMQ endpoint URL (required in production)",
    )

    rabbit_model_upload_topic: Optional[str] = Field(
        default=None,
        validation_alias="RABBIT_MODEL_UPLOAD_TOPIC",
        description="RabbitMQ topic for model upload (required in production)",
    )

    # 데이터셋 경로
    dataset_path: str = Field(
        default="/data",
        validation_alias="DATASET_PATH",
        description="Dataset base path (absolute path)",
    )

    @property
    def is_production(self) -> bool:
        """
        Production 환경 여부 확인.

        Returns:
            bool: PROFILE이 'prod' 또는 'production'이면 True, 그 외 False

        Examples:
            >>> config = TrainConfig()  # PROFILE 미설정
            >>> config.is_production
            False

            >>> import os
            >>> os.environ["PROFILE"] = "prod"
            >>> config = TrainConfig()
            >>> config.is_production
            True

        """
        return self.profile in ["prod", "production"]

    def check_production_vars(self) -> None:
        """
        Production 환경에서 필수 환경변수가 기본값인지 검증.

        로컬 개발 환경에서는 기본값을 사용할 수 있지만, Production 환경에서는
        모든 환경변수가 실제 값으로 설정되어 있어야 합니다.

        Raises:
            ValueError: 기본값이 사용된 필수 환경변수가 있을 때

        Examples:
            >>> config = TrainConfig()  # 환경변수 없이 기본값 사용
            >>> config.check_production_vars()  # ValueError 발생

            >>> # Production 환경변수 설정 후
            >>> import os
            >>> os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow.prod.com"
            >>> os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio.prod.com:9000"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "real-key-id"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "real-secret-key"
            >>> os.environ["MODEL_NAME"] = "my_production_model"
            >>> os.environ["TRAIN_ID"] = "prod-train-123"
            >>> os.environ["RABBIT_ENDPOINT_URL"] = "amqp://rabbitmq.prod.com"
            >>> os.environ["RABBIT_MODEL_UPLOAD_TOPIC"] = "model.upload"
            >>> config = TrainConfig()
            >>> config.check_production_vars()  # 통과 ✅

        """
        errors = []

        # Production에서 검증이 필요한 필드와 기본값 매핑
        model_fields = self.__class__.model_fields
        checks = {
            "mlflow_tracking_uri": {
                "value": self.mlflow_tracking_uri,
                "default": model_fields["mlflow_tracking_uri"].default,
                "message": "기본값이 아닌 실제 URI 필요",
            },
            "mlflow_s3_endpoint_url": {
                "value": self.mlflow_s3_endpoint_url,
                "default": model_fields["mlflow_s3_endpoint_url"].default,
                "message": "None이 아닌 실제 endpoint URL 필요",
            },
            "aws_access_key_id": {
                "value": self.aws_access_key_id.get_secret_value(),
                "default": model_fields["aws_access_key_id"].default.get_secret_value(),
                "message": "기본값이 아닌 실제 자격증명 필요",
            },
            "aws_secret_access_key": {
                "value": self.aws_secret_access_key.get_secret_value(),
                "default": model_fields[
                    "aws_secret_access_key"
                ].default.get_secret_value(),
                "message": "기본값이 아닌 실제 자격증명 필요",
            },
            "model_name": {
                "value": self.model_name,
                "default": model_fields["model_name"].default,
                "message": "기본값이 아닌 실제 모델명 필요",
            },
            "train_id": {
                "value": self.train_id,
                "default": model_fields["train_id"].default,
                "message": "기본값이 아닌 실제 훈련 ID 필요",
            },
            "rabbit_endpoint_url": {
                "value": self.rabbit_endpoint_url,
                "default": model_fields["rabbit_endpoint_url"].default,
                "message": "None이 아닌 실제 RabbitMQ endpoint URL 필요",
            },
            "rabbit_model_upload_topic": {
                "value": self.rabbit_model_upload_topic,
                "default": model_fields["rabbit_model_upload_topic"].default,
                "message": "None이 아닌 실제 RabbitMQ topic 필요",
            },
        }

        for field_name, check in checks.items():
            if check["value"] == check["default"]:
                env_var_name = (
                    model_fields[field_name].validation_alias or field_name.upper()
                )
                errors.append(f"{env_var_name} ({check['message']})")

        if errors:
            error_message = (
                "Production 환경에서 기본값을 사용 중인 환경변수가 있습니다:\n"
                + "\n".join(f"  - {error}" for error in errors)
            )
            raise ValueError(error_message)
