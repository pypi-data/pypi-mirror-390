"""데이터셋 경로 관리를 위한 Path 유틸리티."""

import os
import sys
from pathlib import Path
from typing import Optional, Union

from keynet_train.config.settings import TrainConfig

# Python 3.12+에서는 Path를 직접 상속 가능
if sys.version_info >= (3, 12):
    _PathBase = Path
else:
    _PathBase = type(Path())  # type: ignore


class DatasetPath(_PathBase):  # type: ignore
    """
    데이터셋 경로를 관리하는 Path 클래스.

    TrainConfig의 dataset_path를 기본 경로로 사용하며,
    상대 경로 제공 시 dataset_path를 기준으로 해석합니다.

    성능 최적화:
        - TrainConfig 인스턴스를 클래스 레벨에서 캐싱
        - DATASET_PATH 환경변수 변경 시 자동 재로드

    Examples:
        기본 사용 (환경변수 미설정):
            >>> path = DatasetPath()
            >>> str(path)
            '/data'

        상대 경로 사용:
            >>> path = DatasetPath("train/images")
            >>> str(path)
            '/data/train/images'

        절대 경로 사용:
            >>> path = DatasetPath("/custom/dataset")
            >>> str(path)
            '/custom/dataset'

        환경변수로 기본 경로 변경:
            >>> import os
            >>> os.environ["DATASET_PATH"] = "/mnt/datasets"
            >>> path = DatasetPath("train")
            >>> str(path)
            '/mnt/datasets/train'

    Note:
        - 상대 경로는 dataset_path를 기준으로 해석됩니다
        - 절대 경로는 그대로 사용됩니다
        - Path의 모든 메서드 사용 가능 (exists(), mkdir(), glob() 등)
        - TrainConfig는 캐싱되어 성능 최적화됨

    """

    # 클래스 레벨 캐싱을 위한 변수
    _config: Optional[TrainConfig] = None
    _cached_dataset_path: Optional[str] = None

    @classmethod
    def _get_config(cls) -> TrainConfig:
        """
        캐싱된 TrainConfig 인스턴스를 반환하거나 새로 생성.

        환경변수 DATASET_PATH가 변경된 경우 캐시를 무효화하고
        새 TrainConfig 인스턴스를 생성합니다.

        Returns:
            TrainConfig: 캐싱된 또는 새로 생성된 TrainConfig 인스턴스

        Raises:
            ValueError: TrainConfig 로드 실패 시

        """
        current_dataset_path = os.environ.get("DATASET_PATH")

        # 캐시가 없거나 환경변수가 변경된 경우 재생성
        if cls._config is None or cls._cached_dataset_path != current_dataset_path:
            try:
                cls._config = TrainConfig()
                cls._cached_dataset_path = current_dataset_path
            except Exception as e:
                raise ValueError(f"Failed to load dataset configuration: {e}") from e

        return cls._config

    def __new__(cls, *args: Union[str, Path, "os.PathLike[str]"]) -> "DatasetPath":
        """
        DatasetPath 인스턴스 생성.

        Args:
            *args: 경로 세그먼트 (비어있으면 기본 dataset_path 사용)
                  str, Path, 또는 PathLike 객체 지원

        Returns:
            DatasetPath: 생성된 경로 객체

        Raises:
            ValueError: TrainConfig 로드 실패 시

        """
        # 캐싱된 config 사용
        config = cls._get_config()

        # 인자가 없으면 기본 dataset_path 사용
        if not args:
            args = (config.dataset_path,)
        else:
            # 첫 번째 인자가 상대 경로면 dataset_path를 기준으로 해석
            first_arg = str(args[0])
            if not Path(first_arg).is_absolute():
                base_path = Path(config.dataset_path)
                args = (str(base_path / first_arg), *args[1:])

        # Python 3.12+ 호환성: _raw_paths를 명시적으로 설정
        if sys.version_info >= (3, 12):
            # Python 3.12에서는 object.__new__로 객체를 생성하고
            # _raw_paths를 직접 설정해야 함
            instance = object.__new__(cls)
            instance._raw_paths = args
            instance._resolved = False  # type: ignore
            return instance
        else:
            return super().__new__(cls, *args)  # type: ignore

    def __init__(self, *args: Union[str, Path, "os.PathLike[str]"]) -> None:
        """
        DatasetPath 초기화.

        Python 3.12+에서는 __init__이 호출되므로 _raw_paths를 보존해야 함.
        """
        if sys.version_info >= (3, 12):
            # Python 3.12에서는 __new__에서 이미 _raw_paths를 설정했으므로
            # __init__에서는 아무것도 하지 않음
            pass
        else:
            # Python 3.9-3.11에서는 Path의 __init__ 호출
            super().__init__()  # type: ignore
