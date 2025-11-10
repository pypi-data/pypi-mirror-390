"""프레임워크 독립적인 ONNX 모델 로깅 API."""

import logging
import time
from pathlib import Path
from typing import Any, Optional, Union

import mlflow

from ..clients.onnx import OnnxClient

# onnx_client 인스턴스 생성
onnx_client = OnnxClient()
logger = logging.getLogger(__name__)


def log_onnx_model(
    experiment_name: str,
    onnx_model_path: Union[str, Path],
    run_name: Optional[str] = None,
    model_name: Optional[str] = None,
    signature: Optional["mlflow.models.signature.ModelSignature"] = None,
    input_example: Optional[Union[Any, dict[str, Any]]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """
    프레임워크 독립적인 ONNX 모델 로깅 및 배포.

    PyTorch가 아닌 다른 프레임워크(TensorFlow, JAX, MXNet 등)에서
    학습한 모델을 ONNX로 변환한 후, 이 함수를 사용하여 MLflow에
    로깅하고 추론 서비스에 배포할 수 있습니다.

    이 함수는 @trace_pytorch 데코레이터를 사용할 수 없는 상황에서
    ONNX 모델을 직접 업로드하기 위한 대안입니다.

    Args:
        experiment_name: MLflow 실험 이름
        onnx_model_path: ONNX 모델 파일 경로
        run_name: MLflow 런 이름 (선택사항)
        model_name: 모델 이름 (선택사항, 기본값: 파일명)
        signature: MLflow 모델 시그니처 (선택사항)
        input_example: 입력 예시 (선택사항)
        metadata: 추가 메타데이터 (선택사항)

    Returns:
        Optional[str]: 업로드된 모델 경로 (프로덕션 모드가 아닌 경우)

    사용 예시:
        ```python
        # TensorFlow 모델 사용 예
        import tensorflow as tf
        import tf2onnx

        # TensorFlow 모델을 ONNX로 변환
        model = tf.keras.models.load_model('my_model.h5')
        spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)
        output_path = "model.onnx"

        model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec)
        with open(output_path, "wb") as f:
            f.write(model_proto.SerializeToString())

        # ONNX 모델 로깅 및 업로드
        upload_path = log_onnx_model(
            experiment_name="tensorflow_experiment",
            onnx_model_path=output_path,
            metadata={"framework": "tensorflow", "model_type": "classification"}
        )

        # JAX/Flax 모델 사용 예
        # ... JAX 모델을 ONNX로 변환 ...
        upload_path = log_onnx_model(
            experiment_name="jax_experiment",
            onnx_model_path="jax_model.onnx",
            metadata={"framework": "jax", "optimizer": "adam"}
        )
        ```

    """
    try:
        # 경로 객체로 변환
        onnx_path = Path(onnx_model_path)
        if not onnx_path.exists():
            raise FileNotFoundError(f"ONNX 모델 파일을 찾을 수 없습니다: {onnx_path}")

        # ONNX 파일 검증
        if onnx_path.suffix.lower() != ".onnx":
            logger.warning(f"파일 확장자가 .onnx가 아닙니다: {onnx_path.suffix}")

        # 파일 크기 검증 (최소 크기)
        file_size = onnx_path.stat().st_size
        if file_size < 1024:  # 1KB 미만
            logger.warning(f"ONNX 파일 크기가 매우 작습니다: {file_size} bytes")

        # 모델 이름 설정
        if model_name is None:
            model_name = onnx_path.stem

        # 실험 설정
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"새 실험 생성: {experiment_name}")
        else:
            experiment_id = experiment.experiment_id
            logger.info(f"기존 실험 사용: {experiment_name}")

        start_time = time.time()

        with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run:
            logger.info(f"MLflow 실행 시작 (run_id: {run.info.run_id})")

            # 메타데이터 로깅
            if metadata:
                mlflow.log_params(metadata)

            # 기본 정보 로깅
            file_size_mb = onnx_path.stat().st_size / (1024 * 1024)
            mlflow.log_params(
                {
                    "model_name": model_name,
                    "onnx_file_size_mb": file_size_mb,
                    "source_framework": (
                        metadata.get("framework", "unknown") if metadata else "unknown"
                    ),
                }
            )

            # ONNX 모델을 MLflow에 로깅
            import onnx

            onnx_model = onnx.load(str(onnx_path))
            mlflow.onnx.log_model(
                onnx_model=onnx_model,
                artifact_path="model",
                signature=signature,
                input_example=input_example,
            )
            logger.info("ONNX 모델 MLflow 로깅 완료")

            # onnx_client를 통한 업로드
            try:
                upload_result = onnx_client.upload(onnx_path)
                if upload_result:
                    mlflow.log_param("onnx_upload_path", upload_result)
                    logger.info(f"🚀 ONNX 모델 서비스 업로드 완료: {upload_result}")
                else:
                    logger.warning("⚠️ ONNX 업로드 실패")

            except Exception as e:
                logger.error(f"ONNX 클라이언트 업로드 실패: {e}")
                mlflow.log_param("upload_error", str(e))
                upload_result = None

            # 실행 시간 로깅
            total_time = time.time() - start_time
            mlflow.log_metric("total_execution_time", total_time)

            logger.info(f"🎉 ONNX 모델 로깅 완료 (실행시간: {total_time:.2f}초)")

            return upload_result

    except Exception as e:
        logger.error(f"ONNX 모델 로깅 실패: {e}")
        raise
