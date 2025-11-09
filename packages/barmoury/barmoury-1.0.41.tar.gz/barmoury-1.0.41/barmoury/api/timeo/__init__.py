
import math
from typing import Any
from datetime import datetime

def resolve(model: Any):
    if not hasattr(model, "id"):
        return
    if not getattr(model, "id"):
        resolve_created(model)
    else:
        resolve_updated(model)


def resolve_created(model: Any):
    setattr(model, "created_at", datetime.now())
    resolve_updated(model)


def resolve_updated(model: Any):
    setattr(model, "updated_at", datetime.now())

def date_diff(a: datetime, b: datetime, divider: int) -> int:
    diff = a.timestamp() - b.timestamp()
    neg = diff < 0
    if neg:
        diff = abs(diff)
    return (-math.floor(diff / divider) if neg else math.floor(diff / divider))


def date_diff_in_minutes(a: datetime, b: datetime) -> int:
    return date_diff(a, b, (1000 * 60))