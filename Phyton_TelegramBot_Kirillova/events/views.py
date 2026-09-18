from django.conf import settings

import csv
import io
import json
from datetime import datetime, timedelta

from django.core import signing
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from .models import Events

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from events.serializers import EventsSerializer
from .permissions import IsOwnerOrReadOnly

# соль для подписи токенов, привязанная к проекту
EXPORT_SALT = "events.export.v1"
# срок жизни токена — 15 минут
TOKEN_MAX_AGE = 15 * 60


def make_export_token(telegram_id: int, fmt: str = "csv") -> str:
    """Генерирует подписанный токен для скачивания. Вызывается из бота."""
    return signing.dumps(
        {"telegram_id": telegram_id, "fmt": fmt},
        salt=EXPORT_SALT,
    )


@require_GET
def export_link(request):
    """Внутренний эндпоинт: возвращает готовую ссылку на скачивание.
    """
    secret = request.headers.get("X-Bot-Secret")
    if secret != settings.BOT_INTERNAL_SECRET:
        return JsonResponse({"error": "forbidden"}, status=403)

    telegram_id = request.GET.get("telegram_id")
    fmt = request.GET.get("format", "csv")
    if not telegram_id or not telegram_id.isdigit():
        return JsonResponse({"error": "telegram_id is required"}, status=400)

    token = make_export_token(int(telegram_id), fmt=fmt)
    url = request.build_absolute_uri(f"/events/export/?token={token}")
    return JsonResponse({"url": url, "expires_in": TOKEN_MAX_AGE})


@require_GET
def export_events(request):
    """Эндпоинт: /export/?token=...&format=csv|json

    Возвращает события пользователя в CSV или JSON.
    Пользователь определяется по подписанному токену.
    """
    token = request.GET.get("token")
    if not token:
        return JsonResponse({"error": "token is required"}, status=400)

    try:
        data = signing.loads(token, salt=EXPORT_SALT, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        return JsonResponse({"error": "token expired"}, status=403)
    except signing.BadSignature:
        return JsonResponse({"error": "invalid token"}, status=403)

    telegram_id = data.get("telegram_id")
    fmt = (request.GET.get("format") or data.get("fmt") or "csv").lower()

    if not telegram_id:
        return JsonResponse({"error": "invalid token payload"}, status=403)

    # ВАЖНО: фильтрация по user_id — пользователь видит только свои события
    events = (
        Events.objects
        .filter(user_id=telegram_id)
        .order_by("date", "time")
    )

    if fmt == "json":
        return _events_to_json(events, telegram_id)
    if fmt == "csv":
        return _events_to_csv(events, telegram_id)
    return JsonResponse({"error": "unsupported format"}, status=400)


def _events_to_json(events, telegram_id: int) -> JsonResponse:
    payload = {
        "telegram_id": telegram_id,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "name": e.name,
                "date": e.date.isoformat(),
                "time": e.time.strftime("%H:%M"),
                "details": e.details or "",
                "is_public": bool(getattr(e, "is_public", False)),
            }
            for e in events
        ],
    }
    return JsonResponse(payload, json_dumps_params={"ensure_ascii": False})


def _events_to_csv(events, telegram_id: int) -> HttpResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "name", "date", "time", "details", "is_public"])
    for e in events:
        writer.writerow([...])

    filename = f"events_{telegram_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    response = HttpResponse(
        "\ufeff" + buffer.getvalue(),  # BOM в начале
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class EventsViewSet(viewsets.ModelViewSet):
    """CRUD для событий. Пользователь видит только свои события."""
    serializer_class = EventsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # user_id в Events — это FK на users.id, то есть Telegram ID.
        # Сопоставляем его с текущим залогиненным Django-пользователем через
        # telegram_id (если у вас связана модель User бота с auth.User) —
        # либо, для учебного варианта, просто фильтруем по query-параметру.
        telegram_id = self.request.query_params.get("telegram_id")
        qs = Events.objects.all().order_by("-date", "-time")
        if telegram_id:
            qs = qs.filter(user_id=telegram_id)
        return qs

    def perform_create(self, serializer):
        # при создании обязательно проставляем владельца
        # предполагаем, что у request.user есть поле telegram_id
        telegram_id = getattr(self.request.user, "telegram_id", None)
        if not telegram_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Не удалось определить Telegram ID пользователя.")
        serializer.save(user_id=telegram_id)
