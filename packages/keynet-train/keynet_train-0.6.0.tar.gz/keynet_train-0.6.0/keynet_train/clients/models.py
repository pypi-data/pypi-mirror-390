"""
Pydantic models for Backend API communication.

This module defines data models for request/response with the Backend API.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ArgumentType(str, Enum):
    """Argument type enum for hyperparameters."""

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"


class ArgumentDefinition(BaseModel):
    """
    Definition of a single argument/hyperparameter.

    This will be sent to Backend API as part of uploadKey request.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    type: ArgumentType
    default: Optional[Any] = None
    required: bool = False
    help: Optional[str] = None
    choices: Optional[list[str]] = None


class UploadKeyRequest(BaseModel):
    """
    Request model for uploadKey API endpoint.

    Sent to Backend API to request an upload key for pushing container images.
    """

    model_config = ConfigDict(populate_by_name=True)

    model_name: str = Field(alias="modelName")
    hyper_parameters: list[ArgumentDefinition] = Field(
        default_factory=list,
        alias="hyperParameters",
    )


class UploadKeyCommand(BaseModel):
    """
    Docker commands for tagging and pushing the container image.

    Contains the complete docker tag and push commands with full image paths.
    """

    model_config = ConfigDict(populate_by_name=True)

    tag: str
    push: str


class Model(BaseModel):
    """
    Model information from uploadKey API response.

    Contains the model ID and name associated with the upload.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str


class UploadKeyResponse(BaseModel):
    """
    Response model from uploadKey API endpoint.

    Contains the upload key and command to use for pushing the container image.

    Example:
        {
            "id": 253,
            "projectId": 207,
            "uploadKey": "iw6pu99p6hlp11dwi3taz",
            "model": {
                "id": 42,
                "name": "resnet50-classifier"
            },
            "command": {
                "tag": "docker tag <YOUR_IMAGE:TAG> kitech-harbor.wimcorp.dev/kitech-model/iw6pu99p6hlp11dwi3taz:latest",
                "push": "docker push kitech-harbor.wimcorp.dev/kitech-model/iw6pu99p6hlp11dwi3taz:latest"
            }
        }

    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    project_id: int = Field(alias="projectId")
    upload_key: str = Field(alias="uploadKey")
    model: Model
    command: UploadKeyCommand

    def get_image_reference(self) -> str:
        """
        Extract the full image reference from the push command.

        Returns:
            Full image reference (e.g., "kitech-harbor.wimcorp.dev/kitech-model/iw6pu99p6hlp11dwi3taz:latest")

        Example:
            >>> response.command.push
            'docker push kitech-harbor.wimcorp.dev/kitech-model/iw6pu99p6hlp11dwi3taz:latest'
            >>> response.get_image_reference()
            'kitech-harbor.wimcorp.dev/kitech-model/iw6pu99p6hlp11dwi3taz:latest'

        """
        # Remove "docker push " prefix
        return self.command.push.replace("docker push ", "").strip()


class TrainingProjectBrief(BaseModel):
    """
    Brief information about a training project.

    Received from Backend API when fetching the list of trainable projects.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    summary: str
    task_type: str = Field(alias="taskType")
    author: dict[str, Any]


class PageMeta(BaseModel):
    """
    Pagination metadata for list responses.

    Contains information about total items, current page, and page size.
    """

    model_config = ConfigDict(populate_by_name=True)

    total: int
    page: int
    limit: int
    max_page: int = Field(alias="maxPage")


class FetchTrainableProjectsResponse(BaseModel):
    """
    Response model from fetchTrainableProjects API endpoint.

    Contains a paginated list of training projects with metadata.
    """

    model_config = ConfigDict(populate_by_name=True)

    content: list[TrainingProjectBrief]
    meta: PageMeta
