import random
from typing import Dict, List, Optional

from .config import REQUIRED_FIELDS


def add_services(names: List[str], collection=None) -> int:
    """Add service names to the collection as empty cards.

    Returns number of new services created.
    """
    created = 0
    if collection is None:
        from .db import services as collection

    for name in names:
        if collection.count_documents({"name": name}) == 0:
            collection.insert_one({"name": name, "fields": {}})
            created += 1
    return created


def is_complete(service: Dict) -> bool:
    fields = service.get("fields", {})
    return all(fields.get(f) for f in REQUIRED_FIELDS)


def get_random_incomplete(collection=None) -> Optional[Dict]:
    if collection is None:
        from .db import services as collection
    incomplete = list(collection.find({}))
    incomplete = [s for s in incomplete if not is_complete(s)]
    if not incomplete:
        return None
    return random.choice(incomplete)


def update_service(service_id, fields: Dict[str, str], collection=None) -> None:
    """Update fields of a service card by its identifier."""
    if collection is None:
        from .db import services as collection
    collection.update_one({"_id": service_id}, {"$set": {f"fields.{k}": v for k, v in fields.items()}})
