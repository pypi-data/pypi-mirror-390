"""
Tests for Project list models.

Tests the Pydantic models for fetching trainable projects from Backend API.
"""

from keynet_train.clients.models import (
    FetchTrainableProjectsResponse,
    PageMeta,
    TrainingProjectBrief,
)


class TestTrainingProjectBrief:
    """Test TrainingProjectBrief Pydantic model."""

    def test_create_training_project_brief(self):
        """Test creating TrainingProjectBrief with all fields."""
        project = TrainingProjectBrief(
            id=123,
            title="Image Classification",
            summary="A project for classifying images",
            task_type="classification",
            author={"id": "user-uuid", "displayName": "User Example"},
        )

        assert project.id == 123
        assert project.title == "Image Classification"
        assert project.summary == "A project for classifying images"
        assert project.task_type == "classification"
        assert project.author == {"id": "user-uuid", "displayName": "User Example"}

    def test_deserialize_from_camelcase(self):
        """Test TrainingProjectBrief deserializes from camelCase API response."""
        api_data = {
            "id": 456,
            "title": "Object Detection",
            "summary": "Detecting objects in images",
            "taskType": "detection",
            "author": {"id": "admin-uuid", "displayName": "Admin User"},
        }

        project = TrainingProjectBrief(**api_data)

        assert project.id == 456
        assert project.title == "Object Detection"
        assert project.task_type == "detection"
        assert project.author == {"id": "admin-uuid", "displayName": "Admin User"}

    def test_task_type_values(self):
        """Test various taskType values are accepted."""
        task_types = ["classification", "detection", "segmentation", "regression"]

        for task_type in task_types:
            project = TrainingProjectBrief(
                id=1,
                title="Test",
                summary="Test project",
                task_type=task_type,
                author={"id": "test-uuid", "displayName": "Test User"},
            )
            assert project.task_type == task_type


class TestPageMeta:
    """Test PageMeta Pydantic model."""

    def test_create_page_meta(self):
        """Test creating PageMeta with all fields."""
        meta = PageMeta(
            total=100,
            page=1,
            limit=10,
            max_page=10,
        )

        assert meta.total == 100
        assert meta.page == 1
        assert meta.limit == 10
        assert meta.max_page == 10

    def test_deserialize_from_camelcase(self):
        """Test PageMeta deserializes from camelCase API response."""
        api_data = {
            "total": 50,
            "page": 2,
            "limit": 20,
            "maxPage": 3,
        }

        meta = PageMeta(**api_data)

        assert meta.total == 50
        assert meta.page == 2
        assert meta.limit == 20
        assert meta.max_page == 3


class TestFetchTrainableProjectsResponse:
    """Test FetchTrainableProjectsResponse Pydantic model."""

    def test_create_fetch_trainable_projects_response(self):
        """Test creating FetchTrainableProjectsResponse."""
        project1 = TrainingProjectBrief(
            id=1,
            title="Project 1",
            summary="Summary 1",
            task_type="classification",
            author={"id": "user1-uuid", "displayName": "User One"},
        )
        project2 = TrainingProjectBrief(
            id=2,
            title="Project 2",
            summary="Summary 2",
            task_type="detection",
            author={"id": "user2-uuid", "displayName": "User Two"},
        )
        meta = PageMeta(total=2, page=1, limit=10, max_page=1)

        response = FetchTrainableProjectsResponse(
            content=[project1, project2],
            meta=meta,
        )

        assert len(response.content) == 2
        assert response.content[0].id == 1
        assert response.content[1].id == 2
        assert response.meta.total == 2

    def test_deserialize_from_json(self):
        """Test FetchTrainableProjectsResponse can be deserialized from JSON."""
        json_str = """
        {
            "content": [
                {
                    "id": 10,
                    "title": "Image Classifier",
                    "summary": "Train image classifier",
                    "taskType": "classification",
                    "author": {"id": "ml-uuid", "displayName": "ML Engineer"}
                },
                {
                    "id": 20,
                    "title": "Object Detector",
                    "summary": "Detect objects in images",
                    "taskType": "detection",
                    "author": {"id": "ds-uuid", "displayName": "Data Scientist"}
                }
            ],
            "meta": {
                "total": 2,
                "page": 1,
                "limit": 10,
                "maxPage": 1
            }
        }
        """

        response = FetchTrainableProjectsResponse.model_validate_json(json_str)

        assert len(response.content) == 2
        assert response.content[0].id == 10
        assert response.content[0].task_type == "classification"
        assert response.content[1].id == 20
        assert response.content[1].task_type == "detection"
        assert response.meta.total == 2
        assert response.meta.max_page == 1

    def test_empty_content_list(self):
        """Test FetchTrainableProjectsResponse with empty content list."""
        meta = PageMeta(total=0, page=1, limit=10, max_page=0)
        response = FetchTrainableProjectsResponse(
            content=[],
            meta=meta,
        )

        assert response.content == []
        assert response.meta.total == 0

    def test_deserialize_from_dict(self):
        """Test creating FetchTrainableProjectsResponse from dict."""
        data = {
            "content": [
                {
                    "id": 30,
                    "title": "Segmentation Model",
                    "summary": "Semantic segmentation",
                    "taskType": "segmentation",
                    "author": {"id": "researcher-uuid", "displayName": "Researcher"},
                }
            ],
            "meta": {"total": 1, "page": 1, "limit": 10, "maxPage": 1},
        }

        response = FetchTrainableProjectsResponse(**data)

        assert len(response.content) == 1
        assert response.content[0].id == 30
        assert response.content[0].task_type == "segmentation"
