"""PyTorch 모델 훈련 자동화를 위한 데코레이터."""

import functools
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Optional, Union

import httpx
import mlflow
import mlflow.pytorch
import torch

from ..clients.onnx import OnnxClient

# onnx_client 인스턴스 생성
onnx_client = OnnxClient()
logger = logging.getLogger(__name__)


# ============================================================================
# 유틸리티 함수들
# ============================================================================


def _convert_to_numpy(
    tensor_data: Union[torch.Tensor, dict[str, torch.Tensor], tuple, list],
) -> Union[Any, dict[str, Any]]:
    """PyTorch 텐서를 NumPy 배열로 변환 (MLflow infer_signature 용)."""
    if isinstance(tensor_data, torch.Tensor):
        return tensor_data.detach().cpu().numpy()
    elif isinstance(tensor_data, dict):
        return {key: _convert_to_numpy(value) for key, value in tensor_data.items()}
    elif isinstance(tensor_data, (tuple, list)):
        return [_convert_to_numpy(item) for item in tensor_data]
    else:
        return tensor_data


def _infer_model_schema(
    model: torch.nn.Module, sample_input: Union[torch.Tensor, dict[str, torch.Tensor]]
) -> "mlflow.models.signature.ModelSignature":
    """
    PyTorch 모델로부터 자동으로 입력/출력 스키마 추출.

    Args:
        model: PyTorch 모델
        sample_input: 샘플 입력 (실제 모델 실행용)

    Returns:
        ModelSignature: 자동 추출된 스키마

    """
    from mlflow.models.signature import infer_signature

    model.eval()
    device = next(model.parameters()).device

    # 샘플 입력을 모델과 같은 디바이스로 이동
    if isinstance(sample_input, torch.Tensor):
        sample_input = sample_input.to(device)
    elif isinstance(sample_input, dict):
        sample_input = {k: v.to(device) for k, v in sample_input.items()}

    # 실제 모델 실행하여 출력 확인
    with torch.no_grad():
        if isinstance(sample_input, dict):
            sample_output = model(**sample_input)
        else:
            sample_output = model(sample_input)

    # PyTorch 텐서를 NumPy로 변환
    numpy_input = _convert_to_numpy(sample_input)
    numpy_output = _convert_to_numpy(sample_output)

    # MLflow 자동 추론 사용
    signature = infer_signature(numpy_input, numpy_output)

    logger.info(f"자동 추출된 스키마: {signature}")
    return signature


def _generate_input_output_names(
    signature: "mlflow.models.signature.ModelSignature",
) -> tuple[list[str], list[str]]:
    """
    MLflow signature로부터 input/output 이름들을 생성합니다.

    다양한 MLflow 버전 호환성을 고려합니다.
    """
    input_names: list[str] = []
    output_names: list[str] = []

    # 입력 이름 생성 - 여러 방법 시도
    try:
        # 방법 2: 스키마에서 이름 추출
        if not input_names and hasattr(signature.inputs, "schema"):
            schema = signature.inputs.schema
            if hasattr(schema, "names") and schema.names:
                input_names = list(schema.names)
            elif hasattr(schema, "input_names") and callable(schema.input_names):
                potential_names = schema.input_names()
                if potential_names:
                    input_names = list(potential_names)

        # 방법 3: 텐서 정보에서 추출 시도
        if not input_names:
            try:
                input_spec = str(signature.inputs)
                if "'" in input_spec:  # 'image': Tensor, 'mask': Tensor 형태
                    import re

                    names = re.findall(r"'([^']+)':", input_spec)
                    if names:
                        input_names = names
            except Exception:
                pass

        # 방법 4: 기본 이름 생성
        if not input_names:
            # signature.inputs를 분석하여 개수 추정
            inputs_str = str(signature.inputs)
            if "Tensor" in inputs_str:
                tensor_count = inputs_str.count("Tensor")
                input_names = [f"input_{i}" for i in range(max(1, tensor_count))]
            else:
                input_names = ["input_0"]

    except Exception as e:
        logger.debug(f"입력 이름 생성 중 오류: {e}")
        input_names = ["input_0"]

    # 출력 이름 생성 - 유사한 방법들
    try:
        # MLflow outputs는 일반적으로 input_names 메서드가 없음
        if hasattr(signature.outputs, "schema"):
            schema = signature.outputs.schema
            if hasattr(schema, "names") and schema.names:
                output_names = list(schema.names)

        # 기본 이름 생성
        if not output_names:
            outputs_str = str(signature.outputs)
            if "Tensor" in outputs_str:
                tensor_count = outputs_str.count("Tensor")
                output_names = [f"output_{i}" for i in range(max(1, tensor_count))]
            else:
                output_names = ["output_0"]

    except Exception as e:
        logger.debug(f"출력 이름 생성 중 오류: {e}")
        output_names = ["output_0"]

    logger.debug(f"생성된 이름 - 입력: {input_names}, 출력: {output_names}")
    return input_names, output_names


def _convert_pytorch_to_onnx_with_client(
    model: torch.nn.Module,
    sample_input: Union[torch.Tensor, dict[str, torch.Tensor]],
    signature: "mlflow.models.signature.ModelSignature",
    onnx_opset_version: int = 17,
    custom_dynamic_axes: Optional[dict[str, dict[int, str]]] = None,
) -> Optional[str]:
    """
    PyTorch 모델을 ONNX로 변환하고 onnx_client를 통해 업로드합니다.

    Args:
        model: PyTorch 모델
        sample_input: 샘플 입력
        signature: MLflow 시그니처
        onnx_opset_version: ONNX opset 버전
        custom_dynamic_axes: 사용자 정의 dynamic_axes (선택사항)

    Returns:
        Optional[str]: 업로드된 모델 경로 (프로덕션 모드가 아닌 경우)

    """
    try:
        # 스키마로부터 input/output 이름 자동 생성
        input_names, output_names = _generate_input_output_names(signature)

        logger.info(f"ONNX 변환 시작 - 입력: {input_names}, 출력: {output_names}")

        # 임시 ONNX 파일 생성
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as tmp_file:
            onnx_path = tmp_file.name

        conversion_start = time.time()

        # 🎯 개선된 dynamic_axes 구성
        dynamic_axes = {}

        # 1. 기본 배치 차원 설정 (모든 입력/출력에 적용)
        for input_name in input_names:
            dynamic_axes[input_name] = {0: "batch_size"}

        for output_name in output_names:
            dynamic_axes[output_name] = {0: "batch_size"}

        # 2. 사용자 정의 dynamic_axes 병합
        if custom_dynamic_axes:
            for tensor_name, axes_dict in custom_dynamic_axes.items():
                if tensor_name in dynamic_axes:
                    # 기존 축 정보와 병합
                    dynamic_axes[tensor_name].update(axes_dict)
                else:
                    # 새로운 텐서 추가
                    dynamic_axes[tensor_name] = axes_dict.copy()

        logger.info(f"최종 Dynamic axes 구성: {dynamic_axes}")

        # PyTorch → ONNX 변환 (호환성 우선)
        # sample_input을 적절한 형태로 변환
        export_args: Any
        if isinstance(sample_input, torch.Tensor):
            export_args = (sample_input,)
        elif isinstance(sample_input, dict):
            # dict 형태의 입력은 그대로 사용
            export_args = sample_input
        else:
            export_args = sample_input

        try:
            # 동적 크기 지원 시도
            torch.onnx.export(
                model,
                export_args,  # type: ignore[arg-type]
                onnx_path,
                export_params=True,
                opset_version=onnx_opset_version,
                do_constant_folding=True,
                input_names=input_names,
                output_names=output_names,
                dynamic_axes=dynamic_axes,
                verbose=False,
            )
            logger.info("동적 크기 ONNX 모델 변환 완료")

        except Exception as e:
            # 고정 크기로 재시도 (dynamic_axes 제거)
            logger.warning(
                f"동적 크기 ONNX 변환 실패, 고정 크기로 재시도: {str(e)[:100]}..."
            )
            try:
                torch.onnx.export(
                    model,
                    export_args,  # type: ignore[arg-type]
                    onnx_path,
                    export_params=True,
                    opset_version=onnx_opset_version,
                    do_constant_folding=True,
                    input_names=input_names,
                    output_names=output_names,
                    verbose=False,
                )
                logger.info("고정 크기 ONNX 모델 변환 완료")
            except Exception as e2:
                # 최소한의 설정으로 마지막 시도
                logger.warning(
                    f"표준 ONNX 변환도 실패, 최소 설정으로 재시도: {str(e2)[:100]}..."
                )
                torch.onnx.export(
                    model,
                    export_args,  # type: ignore[arg-type]
                    onnx_path,
                    export_params=True,
                    opset_version=onnx_opset_version,
                )
                logger.info("최소 설정 ONNX 모델 변환 완료")

        conversion_time = time.time() - conversion_start

        onnx_path_obj = Path(onnx_path)
        if not onnx_path_obj.exists():
            raise FileNotFoundError("ONNX 파일이 생성되지 않았습니다.")

        file_size_mb = onnx_path_obj.stat().st_size / (1024 * 1024)

        # ONNX 메타데이터 로깅
        onnx_metadata = {
            "onnx_conversion_time": conversion_time,
            "onnx_file_size_mb": file_size_mb,
            "onnx_opset_version": onnx_opset_version,
        }
        mlflow.log_metrics(onnx_metadata)
        mlflow.log_params(
            {
                "onnx_input_names": input_names,
                "onnx_output_names": output_names,
            }
        )

        logger.info(f"ONNX 변환 완료: {onnx_path} ({file_size_mb:.2f}MB)")

        # 🔥 onnx_client를 통한 업로드 및 RabbitMQ 발행
        try:
            upload_result = onnx_client.upload(onnx_path)
            logger.info("✅ ONNX 모델 업로드 및 RabbitMQ 발행 완료")

            # 임시 파일 정리
            onnx_path_obj.unlink()

            return upload_result

        except Exception as e:
            logger.error(f"ONNX 클라이언트 업로드 실패: {e}")
            # 임시 파일 정리
            if onnx_path_obj.exists():
                onnx_path_obj.unlink()
            raise

    except Exception as e:
        logger.error(f"ONNX 변환 실패: {e}")
        mlflow.log_param("onnx_conversion_error", str(e))
        return None


def trace_pytorch(
    model_name: str,
    sample_input: Union[torch.Tensor, dict[str, torch.Tensor]],
    run_name: Optional[str] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    onnx_opset_version: int = 17,
    auto_convert_onnx: bool = True,
    log_model_info: bool = True,
    enable_autolog: bool = True,
    base_image: Optional[str] = None,
    dynamic_axes: Optional[dict[str, dict[int, str]]] = None,
):
    """
    완전 자동화된 PyTorch 모델 추적 (experiment 이름 자동 생성).

    실험 이름은 환경변수 MODEL_ID와 model_name으로 자동 구성됩니다:
    - MODEL_ID 존재: "{model_id}_{model_name}" (예: "42_resnet50-classifier")
    - MODEL_ID 없음: "{model_name}" (예: "resnet50-classifier")

    자동화 범위:
        ✅ 자동 처리:
            - MLflow 실험 이름 자동 생성 (MODEL_ID + model_name)
            - MLflow 실험/런 생성 및 관리
            - 모델 스키마 자동 추론 (실제 모델 실행)
            - 모델 아티팩트 자동 로깅 (enable_autolog=True 시)
            - PyTorch → ONNX 자동 변환
            - S3/MinIO 자동 업로드
            - RabbitMQ 메시지 발행
            - Triton config.pbtxt 생성

        📝 수동 처리 필요:
            - 학습 메트릭 로깅 (mlflow.log_metric())
            - 하이퍼파라미터 로깅 (mlflow.log_params())
            - 커스텀 아티팩트/태그

    Args:
        model_name: 모델 이름 (필수)
            - experiment_name 자동 구성에 사용
            - MLflow에 기록되고, `keynet-train push`에서 uploadKey의 modelName으로 사용
            - 명시적으로 선언하여 모델의 의도를 명확히 표현
            - CLI `--model-name` 옵션으로 override 가능
            - 예: "resnet50-classifier", "bert-sentiment-analyzer"
        sample_input: 샘플 입력 (torch.Tensor 또는 Dict[str, torch.Tensor])
            - Tensor: 단일 입력, ONNX 입력명 "input_0"
            - Dict: 다중 입력, 딕셔너리 키가 ONNX 입력명으로 사용 (권장)
        run_name: MLflow 런 이름 (선택사항)
        device: 디바이스 ("cuda" 또는 "cpu")
        onnx_opset_version: ONNX opset 버전 (기본값: 17)
        auto_convert_onnx: PyTorch → ONNX 자동 변환 여부 (기본값: True)
        log_model_info: 모델 정보 로깅 여부 (기본값: True)
        enable_autolog: MLflow autolog 활성화 여부 (기본값: True)
            - True: 모델 아티팩트 자동 로깅
            - False: 모델도 수동 로깅 필요
            - 주의: 메트릭은 True/False 상관없이 항상 수동 로깅 필요
        base_image: 컨테이너 베이스 이미지 (선택사항)
            - 지정하면 MLflow에 기록되고, `keynet-train push`에서 자동 사용
            - 예: "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"
            - `keynet-train push --dockerfile`로 커스텀 Dockerfile 사용 시 무시됨
            - CLI `--base-image` 옵션이 이 값보다 우선함
        dynamic_axes: 사용자 정의 dynamic_axes (선택사항)
            - 기본적으로 배치 차원(0번)은 자동으로 동적 크기 설정
            - 추가 차원 가변 설정이 필요한 경우 사용

    Returns:
        함수 decorator

    Raises:
        ValueError: 함수가 torch.nn.Module 이외의 객체를 반환하는 경우

    Environment Variables:
        MODEL_ID: (선택사항) 모델 ID, experiment_name 구성에 사용
            - 설정됨: experiment = "{MODEL_ID}_{model_name}"
            - 설정 안됨: experiment = "{model_name}"
            - 로컬 개발: 없음 (model_name만 사용)
            - 프로덕션: 백엔드에서 주입 가능

    Note:
        - 데코레이팅된 함수는 반드시 torch.nn.Module 객체만 반환해야 합니다
        - enable_autolog=True일 때도 학습 메트릭은 수동으로 로깅해야 합니다
        - autolog는 모델 파라미터와 아티팩트만 자동 로깅합니다
        - mlflow.log_metric(), mlflow.log_params()는 데코레이터 내부에서 직접 호출하세요

    사용 예시:
        ```python
        # 로컬 개발 (MODEL_ID 없음)
        @trace_pytorch(
            model_name="resnet50-classifier",
            sample_input=torch.randn(1, 3, 224, 224)
        )
        def train_model():
            model = MyModel()
            # 학습 코드...
            return model
        # Experiment 이름: "resnet50-classifier"

        # 프로덕션 (MODEL_ID=42)
        # export MODEL_ID=42
        @trace_pytorch(
            model_name="resnet50-classifier",
            sample_input=torch.randn(1, 3, 224, 224)
        )
        def train_model():
            model = MyModel()
            # 학습 코드...
            return model
        # Experiment 이름: "42_resnet50-classifier"

        # 다중 입력 모델
        @trace_pytorch(
            model_name="unet-segmentation",
            sample_input={"image": torch.randn(1, 3, 224, 224), "mask": torch.randn(1, 1, 224, 224)}
        )
        def train_multi_input_model():
            model = MultiInputModel()
            # 학습 코드...
            return model

        # 베이스 이미지 지정
        @trace_pytorch(
            model_name="resnet50-classifier",
            sample_input=torch.randn(1, 3, 224, 224),
            base_image="pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"
        )
        def train_model():
            model = MyModel()
            # 학습 코드...
            return model
        ```

    """
    # 디바이스 검증
    if not torch.cuda.is_available() and device == "cuda":
        logger.warning("CUDA가 사용 불가하므로 CPU로 변경합니다.")
        device = "cpu"

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # MODEL_ID와 model_name으로 experiment_name 자동 생성
            from keynet_train.config.settings import TrainConfig
            from keynet_train.utils.experiment import generate_experiment_name

            config = TrainConfig()
            experiment_name = generate_experiment_name(
                model_id=config.model_id, model_name=model_name
            )

            if enable_autolog:
                mlflow.pytorch.autolog()
                logger.info("✅ MLflow PyTorch autolog 활성화 완료")
            else:
                mlflow.pytorch.autolog(disable=True)
                logger.info("🚫 MLflow PyTorch autolog 비활성화")

            # 실험 설정
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"새 실험 생성: {experiment_name}")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"기존 실험 사용: {experiment_name}")

            start_time = time.time()

            with mlflow.start_run(
                experiment_id=experiment_id, run_name=run_name
            ) as run:
                try:
                    # SpringBoot 서버로 MlFlow run_id 전송
                    run_uuid = run.info.run_id
                    train_id = os.environ.get("TRAIN_ID")
                    training_match_end_point = os.environ.get(
                        "APP_TRAINING_MATCH_ENDPOINT"
                    )
                    api_key = os.environ.get("APP_API_KEY")

                    if training_match_end_point and train_id and api_key:
                        # 재시도 설정: 1, 2, 4, 8, 16초 간격으로 5번 시도
                        max_retries = 5
                        retry_delay = 1

                        for attempt in range(max_retries):
                            try:
                                api_url = training_match_end_point.replace(
                                    "{train_id}", train_id
                                ).replace("{run_uuid}", run_uuid)
                                logger.debug(
                                    f"🔗 MLflow run_id 서버 전송 시도 {attempt + 1}/{max_retries}: {api_url}"
                                )
                                headers = {"X-INTERNAL-API-KEY": api_key}
                                response = httpx.patch(
                                    api_url, headers=headers, timeout=10.0
                                )
                                response.raise_for_status()
                                logger.info(
                                    f"✅ MLflow run_id를 서버로 전송 완료: trainId - {train_id} | runUuid - {run_uuid}"
                                )
                                break  # 성공 시 루프 탈출
                            except httpx.HTTPError as e:
                                if (
                                    attempt < max_retries - 1
                                ):  # 마지막 시도가 아니면 재시도
                                    logger.warning(
                                        f"⚠️ MLflow run_id 서버 전송 실패 (시도 {attempt + 1}/{max_retries}), {retry_delay}초 후 재시도: {e}"
                                    )
                                    time.sleep(retry_delay)
                                    retry_delay *= 2  # 지수 백오프
                                else:  # 마지막 시도도 실패
                                    logger.error(
                                        f"⚠️ MLflow run_id 서버 전송 실패 (모든 재시도 소진, 계속 진행): {e}"
                                    )
                    else:
                        logger.warning("MLflow run_id 서버 전송 스킵 (환경변수 미설정)")

                    logger.info(f"MLflow 실행 시작 (run_id: {run_uuid})")

                    # Log model_name if provided
                    if model_name:
                        mlflow.log_param("model_name", model_name)
                        logger.info(f"Model name: {model_name}")

                    # Log base_image if provided
                    if base_image:
                        mlflow.log_param("container_base_image", base_image)
                        logger.info(f"Container base image: {base_image}")

                    # 사용자 함수 실행
                    result = func(*args, **kwargs)

                    # 반환값 검증 - 모델만 반환해야 함!
                    if not isinstance(result, torch.nn.Module):
                        raise ValueError(
                            "함수는 torch.nn.Module만 반환해야 합니다.\n"
                            f"받은 타입: {type(result)}\n"
                            "예시: return model"
                        )

                    model = result

                    # 모델을 지정된 디바이스로 이동
                    model = model.to(device)
                    logger.info(f"모델이 {device} 디바이스로 이동되었습니다.")

                    # sample_input도 동일한 디바이스로 이동
                    if isinstance(sample_input, torch.Tensor):
                        device_sample_input = sample_input.to(device)
                    elif isinstance(sample_input, dict):
                        device_sample_input = {
                            k: v.to(device) for k, v in sample_input.items()
                        }
                    else:
                        raise ValueError(
                            f"지원되지 않는 sample_input 타입: {type(sample_input)}"
                        )

                    # 🚀 핵심: 실제 모델로부터 스키마 자동 추출
                    signature = _infer_model_schema(model, device_sample_input)

                    # 모델 정보 로깅
                    if log_model_info:
                        model_info = {
                            "model_class": model.__class__.__name__,
                            "device": str(device),
                            "total_params": sum(p.numel() for p in model.parameters()),
                            "trainable_params": sum(
                                p.numel() for p in model.parameters() if p.requires_grad
                            ),
                        }

                        # 입력 정보 자동 추출
                        if isinstance(device_sample_input, torch.Tensor):
                            model_info["input_shape"] = tuple(device_sample_input.shape)
                            model_info["input_dtype"] = str(device_sample_input.dtype)
                        elif isinstance(device_sample_input, dict):
                            model_info["input_shapes"] = {
                                k: tuple(v.shape)
                                for k, v in device_sample_input.items()
                            }
                            model_info["input_dtypes"] = {
                                k: str(v.dtype) for k, v in device_sample_input.items()
                            }

                        mlflow.log_params(model_info)
                        logger.info(f"모델 정보 로깅 완료: {model_info['model_class']}")

                    # 🤝 Autolog와 수동 로깅의 조화
                    # autolog가 활성화되어 있으면 중복 로깅 방지
                    if not enable_autolog:
                        # autolog가 비활성화된 경우에만 수동으로 모델 로깅
                        model_info = mlflow.pytorch.log_model(
                            pytorch_model=model,
                            artifact_path="model",
                            signature=signature,
                            input_example=_convert_to_numpy(device_sample_input),
                        )
                        logger.info("PyTorch 모델 수동 로깅 완료")
                    else:
                        logger.info("PyTorch 모델은 autolog에 의해 자동 로깅됩니다")

                    # 🔥 ONNX 변환 및 업로드 (onnx_client 활용)
                    if auto_convert_onnx:
                        upload_result = _convert_pytorch_to_onnx_with_client(
                            model=model,
                            sample_input=device_sample_input,
                            signature=signature,
                            onnx_opset_version=onnx_opset_version,
                            custom_dynamic_axes=dynamic_axes,
                        )

                        if upload_result:
                            mlflow.log_param("onnx_upload_path", upload_result)
                            mlflow.log_param("custom_dynamic_axes", str(dynamic_axes))
                            logger.info(
                                f"🚀 ONNX 모델 서비스 업로드 완료: {upload_result}"
                            )
                        else:
                            logger.warning("⚠️ ONNX 업로드 실패")

                    # 실행 시간 로깅
                    total_time = time.time() - start_time
                    mlflow.log_metric("total_execution_time", total_time)

                    logger.info(f"🎉 모델 추적 완료 (실행시간: {total_time:.2f}초)")
                    logger.info(f"자동 추출된 스키마: {signature}")

                    return model

                except Exception as e:
                    logger.error(f"모델 추적 실패: {e}")
                    mlflow.log_param("execution_error", str(e))
                    raise

        return wrapper

    return decorator
