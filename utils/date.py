from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.utils.timezone import is_naive, make_aware


def to_aware(dt_str):
    parsed = parse_datetime(dt_str)

    if parsed is None:
        return None

    if is_naive(parsed):
        return make_aware(parsed, timezone.get_current_timezone())

    return parsed
