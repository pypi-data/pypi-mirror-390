"""Base MLflow client with TrainConfig integration."""

import logging
import os
from abc import ABCMeta, abstractmethod

import numpy as np
import onnx
import pika

from ..config import TrainConfig

logger = logging.getLogger(__name__)


class BaseMLflowClient(metaclass=ABCMeta):
    """
    Base MLflow client for model upload and logging.

    This client integrates with TrainConfig for environment variable management.
    It supports both development and production modes based on the PROFILE environment variable.

    Development mode (PROFILE not set or not 'prod'/'production'):
        - Uses default values from TrainConfig
        - Automatically sets environment variables if not present
        - No validation required

    Production mode (PROFILE='prod' or 'production'):
        - Validates all required environment variables via TrainConfig.check_production_vars()
        - Requires actual credentials (not defaults)
        - Requires RabbitMQ configuration

    Examples:
        >>> # Development mode (no env vars required)
        >>> client = BaseMLflowClient()
        >>> # Uses default MLflow URI: http://localhost:5000

        >>> # Production mode (all env vars required)
        >>> os.environ["PROFILE"] = "prod"
        >>> os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow.prod.com"
        >>> # ... set all other required env vars ...
        >>> client = BaseMLflowClient()  # Validates all env vars

    """

    ONNX_TO_TRITON_DTYPE = {
        onnx.TensorProto.BOOL: "TYPE_BOOL",
        onnx.TensorProto.UINT8: "TYPE_UINT8",
        onnx.TensorProto.UINT16: "TYPE_UINT16",
        onnx.TensorProto.UINT32: "TYPE_UINT32",
        onnx.TensorProto.UINT64: "TYPE_UINT64",
        onnx.TensorProto.INT8: "TYPE_INT8",
        onnx.TensorProto.INT16: "TYPE_INT16",
        onnx.TensorProto.INT32: "TYPE_INT32",
        onnx.TensorProto.INT64: "TYPE_INT64",
        onnx.TensorProto.FLOAT16: "TYPE_FP16",
        onnx.TensorProto.FLOAT: "TYPE_FP32",
        onnx.TensorProto.DOUBLE: "TYPE_FP64",
        onnx.TensorProto.STRING: "TYPE_STRING",
        # Brain floating point (bfloat16) is not directly supported in ONNX, you might need to handle it separately
        # "TYPE_BF16": <corresponding ONNX type if available or a custom handler>
    }

    def __init__(self):
        """
        Initialize BaseMLflowClient with TrainConfig integration.

        This method:
        1. Loads configuration from TrainConfig (auto-loads from env vars)
        2. Determines production mode based on config.is_production
        3. In production mode: validates all required env vars
        4. Sets os.environ for MLflow (only if not already set)
        5. Stores internal values from config

        Raises:
            ValueError: If production mode and required env vars are missing or using defaults

        """
        # Load configuration (auto-loads from environment variables)
        config = TrainConfig()

        # Determine production mode from PROFILE
        self.is_production = config.is_production

        if not self.is_production:
            # Development mode
            logging.warning(
                """
                You are using a non-production profile.
                If you are in production, please set the PROFILE environment variable to 'prod' or 'production'.
                """
            )

            # CRITICAL: MLflow reads from os.environ directly
            # Only set env vars if they don't exist (to avoid overriding user settings)
            if os.environ.get("MLFLOW_TRACKING_URI") is None:
                os.environ["MLFLOW_TRACKING_URI"] = config.mlflow_tracking_uri

            if (
                os.environ.get("MLFLOW_S3_ENDPOINT_URL") is None
                and config.mlflow_s3_endpoint_url
            ):
                os.environ["MLFLOW_S3_ENDPOINT_URL"] = config.mlflow_s3_endpoint_url

            if os.environ.get("AWS_ACCESS_KEY_ID") is None:
                os.environ["AWS_ACCESS_KEY_ID"] = (
                    config.aws_access_key_id.get_secret_value()
                )

            if os.environ.get("AWS_SECRET_ACCESS_KEY") is None:
                os.environ["AWS_SECRET_ACCESS_KEY"] = (
                    config.aws_secret_access_key.get_secret_value()
                )

            # Model metadata (development defaults)
            self.model_name = config.model_name
            self.train_id = config.train_id

        else:
            # Production mode - validate all required env vars
            config.check_production_vars()

            # Set env vars for MLflow (only if not already set)
            if os.environ.get("MLFLOW_TRACKING_URI") is None:
                os.environ["MLFLOW_TRACKING_URI"] = config.mlflow_tracking_uri

            if (
                os.environ.get("MLFLOW_S3_ENDPOINT_URL") is None
                and config.mlflow_s3_endpoint_url
            ):
                os.environ["MLFLOW_S3_ENDPOINT_URL"] = config.mlflow_s3_endpoint_url

            if os.environ.get("AWS_ACCESS_KEY_ID") is None:
                os.environ["AWS_ACCESS_KEY_ID"] = (
                    config.aws_access_key_id.get_secret_value()
                )

            if os.environ.get("AWS_SECRET_ACCESS_KEY") is None:
                os.environ["AWS_SECRET_ACCESS_KEY"] = (
                    config.aws_secret_access_key.get_secret_value()
                )

            # Production-required fields
            self.model_name = config.model_name
            self.train_id = config.train_id
            self._uploadModelExchange = config.rabbit_model_upload_topic

            # RabbitMQ endpoint (for get_connection method)
            if (
                os.environ.get("RABBIT_ENDPOINT_URL") is None
                and config.rabbit_endpoint_url
            ):
                os.environ["RABBIT_ENDPOINT_URL"] = (
                    config.rabbit_endpoint_url.get_secret_value()
                )

    def get_connection(self):
        """
        Create RabbitMQ connection.

        Returns:
            pika.BlockingConnection: RabbitMQ connection

        Raises:
            KeyError: If RABBIT_ENDPOINT_URL env var is not set

        """
        return pika.BlockingConnection(
            pika.URLParameters(os.environ["RABBIT_ENDPOINT_URL"])
        )

    def get_triton_compatible_type(self, tensor_type):
        """
        Convert ONNX tensor type to Triton-compatible type string.

        Args:
            tensor_type: ONNX tensor type

        Returns:
            str: Triton type string (e.g., "TYPE_FP32", "TYPE_INT64")

        """
        return self.ONNX_TO_TRITON_DTYPE.get(tensor_type.elem_type, "UNKNOWN")

    @abstractmethod
    def upload(self, model):
        """
        Upload model to storage.

        Args:
            model: Model to upload

        """
        pass

    @abstractmethod
    def _log_tensor(self, model):
        """
        Log tensor information of the model.

        Args:
            model: Model to log tensor info from

        """
        pass

    @abstractmethod
    def _log_model(self, model, input_example: np.ndarray) -> str:
        """
        Log model to MLflow.

        Args:
            model: Model to log
            input_example: Input example for automatic signature inference

        Returns:
            str: Path to the logged model

        """
        pass
