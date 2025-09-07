from typing import Any, Dict, List
import uuid

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot import service_repository as repo
from bot.config import REQUIRED_FIELDS


class InMemoryCollection:
    """Minimal in-memory stand-in for a MongoDB collection."""

    def __init__(self):
        self.data: List[Dict[str, Any]] = []

    def insert_one(self, doc: Dict[str, Any]) -> None:
        doc = dict(doc)
        doc.setdefault("_id", uuid.uuid4().hex)
        self.data.append(doc)

    def find(self, filter: Dict[str, Any] | None = None):
        if not filter:
            return list(self.data)
        return [d for d in self.data if all(d.get(k) == v for k, v in filter.items())]

    def find_one(self, filter: Dict[str, Any]):
        results = self.find(filter)
        return results[0] if results else None

    def count_documents(self, filter: Dict[str, Any]):
        return len(self.find(filter))

    def update_one(self, filter: Dict[str, Any], update: Dict[str, Any]):
        doc = self.find_one(filter)
        if not doc:
            return
        for k, v in update.get("$set", {}).items():
            parts = k.split(".")
            target = doc
            for part in parts[:-1]:
                target = target.setdefault(part, {})
            target[parts[-1]] = v


def test_add_and_complete_flow():
    col = InMemoryCollection()
    added = repo.add_services(["s1", "s2"], collection=col)
    assert added == 2
    added = repo.add_services(["s1"], collection=col)
    assert added == 0

    card = repo.get_random_incomplete(collection=col)
    assert card is not None
    service_id = card["_id"]

    fields = {f: f"value_{f}" for f in REQUIRED_FIELDS}
    repo.update_service(service_id, fields, collection=col)

    card = col.find_one({"_id": service_id})
    assert repo.is_complete(card)
