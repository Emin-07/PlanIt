import pytest
from fastapi.testclient import TestClient

from tests.helpers.auth import get_auth_headers_for_test_user

# from schemas import PriorityEnum


class TestTaskEndpoints:
    """Test task-related endpoints."""

    @pytest.mark.asyncio
    async def test_create_task(
        self, client: TestClient, test_user, task_create_data: dict
    ):
        """Test creating a new task."""
        headers = get_auth_headers_for_test_user(client, test_user)

        response = client.post("/tasks/", json=task_create_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_create_data["title"]
        assert data["user_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_task_unauthorized(
        self, client: TestClient, task_create_data: dict
    ):
        """Test creating task without authentication."""
        print(f"Client headers: {client.headers}")
        response = client.post("/tasks/", json=task_create_data)

        assert response.status_code == 401

    # @pytest.mark.asyncio
    # async def test_get_task(self, client: TestClient, test_user, test_task):
    #     """Test retrieving a single task."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.get(f"/tasks/{test_task.id}", headers=headers)

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["id"] == test_task.id
    #     assert data["title"] == test_task.title
    #     assert data["user_id"] == test_user.id

    # @pytest.mark.asyncio
    # async def test_get_nonexistent_task(self, client: TestClient, test_user):
    #     """Test retrieving a task that doesn't exist."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.get("/tasks/99999", headers=headers)
    #     assert response.status_code == 404

    # @pytest.mark.asyncio
    # async def test_list_tasks(self, client: TestClient, test_user, multiple_tasks):
    #     """Test listing tasks with pagination."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.get(
    #         "/tasks/", params={"limit": 2, "offset": 0}, headers=headers
    #     )

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert "items" in data
    #     assert "total" in data
    #     assert "page" in data
    #     assert len(data["items"]) <= 2  # Should respect limit

    # @pytest.mark.asyncio
    # async def test_list_tasks_with_filters(
    #     self, client: TestClient, test_user, multiple_tasks
    # ):
    #     """Test listing tasks with completion filter."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     # Filter by completed tasks
    #     response = client.get("/tasks/", params={"is_completed": True}, headers=headers)

    #     assert response.status_code == 200
    #     data = response.json()
    #     for task in data["items"]:
    #         assert task["is_completed"] is True

    # @pytest.mark.asyncio
    # async def test_list_tasks_with_priority_filter(
    #     self, client: TestClient, test_user, multiple_tasks
    # ):
    #     """Test listing tasks with priority filter."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.get(
    #         "/tasks/",
    #         params={"priority": PriorityEnum.HIGH.value},
    #         headers=headers,
    #     )

    #     assert response.status_code == 200
    #     data = response.json()
    #     for task in data["items"]:
    #         assert task["priority"] == PriorityEnum.HIGH.value

    # @pytest.mark.asyncio
    # async def test_update_task(
    #     self, client: TestClient, test_user, test_task, task_update_data: dict
    # ):
    #     """Test updating a task."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.patch(
    #         f"/tasks/{test_task.id}", json=task_update_data, headers=headers
    #     )

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["title"] == task_update_data["title"]
    #     assert data["is_completed"] == task_update_data["is_completed"]
    #     assert data["description"] == task_update_data["description"]

    # @pytest.mark.asyncio
    # async def test_update_task_unauthorized(
    #     self, client: TestClient, test_task, task_update_data: dict
    # ):
    #     """Test updating task without authentication."""
    #     response = client.patch(f"/tasks/{test_task.id}", json=task_update_data)
    #     assert response.status_code == 401

    # @pytest.mark.asyncio
    # async def test_update_other_users_task(
    #     self, client: TestClient, test_user, tasks_for_multiple_users: dict
    # ):
    #     """Test updating another user's task (should fail)."""
    #     # Get a task belonging to a different user
    #     other_user_id = next(
    #         uid for uid in tasks_for_multiple_users.keys() if uid != test_user.id
    #     )
    #     other_user_task = tasks_for_multiple_users[other_user_id][0]

    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.patch(
    #         f"/tasks/{other_user_task.id}",
    #         json={"title": "Hacked title"},
    #         headers=headers,
    #     )

    #     # Should return 403 Forbidden or 404 Not Found
    #     assert response.status_code in [403, 404]

    # @pytest.mark.asyncio
    # async def test_delete_task(self, client: TestClient, test_user, test_task):
    #     """Test deleting a task."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.delete(
    #         "/tasks/", params={"task_id": test_task.id}, headers=headers
    #     )

    #     assert response.status_code == 204

    #     # Verify task is deleted
    #     get_response = client.get(f"/tasks/{test_task.id}", headers=headers)
    #     assert get_response.status_code == 404

    # @pytest.mark.asyncio
    # async def test_mark_task_complete(self, client: TestClient, test_user, test_task):
    #     """Test marking a task as complete."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.post(f"/tasks/{test_task.id}/complete", headers=headers)

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["is_completed"] is True

    # @pytest.mark.asyncio
    # async def test_get_tasks_summary(
    #     self, client: TestClient, test_user, multiple_tasks
    # ):
    #     """Test getting task statistics/summary."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.get("/tasks/summary", headers=headers)

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert "total_tasks" in data
    #     assert "completed_tasks" in data
    #     assert "pending_tasks" in data
    #     assert "high_priority_tasks" in data
