import json
from datetime import datetime, date
from decimal import Decimal
import uuid


def default_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    if hasattr(obj, 'model_dump') and callable(obj.model_dump):
        return obj.model_dump()
    return str(obj)

def dumps(data, *, indent=None, sort_keys=False):
    return json.dumps(
        data,
        default=default_serializer,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=False,
    )


def loads(s):
    return json.loads(s)
