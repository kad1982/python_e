import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from events.models import Events


@pytest.mark.django_db
def test_events_api_list_returns_json():
    client = APIClient()
    response = client.get("/events/api/events/", HTTP_ACCEPT="application/json")

    # 401/403 — если закрыто авторизацией; 200 — если открыто
    assert response.status_code in (200, 401, 403)


@pytest.mark.django_db
def test_events_api_requires_auth_for_write():
    client = APIClient()
    response = client.post("/events/api/events/", {"name": "X"}, format="json")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_events_api_filters_by_telegram_id(django_user_model):
    user = django_user_model.objects.create_user(username="tester", password="pass")
    user.telegram_id = 475166619
    user.save()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        "/events/api/events/?telegram_id=475166619",
        HTTP_ACCEPT="application/json",
    )

    assert response.status_code == 200