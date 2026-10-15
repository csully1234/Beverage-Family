"""Discovery matching only: no spelling rule changes historical identities."""
import json
import re
import unicodedata
from difflib import SequenceMatcher

VARIANTS = {word: "beverage" for word in ("beverage", "beveridge", "beveredge", "bevridge", "bevrage", "beseridge")}
VARIANTS.update({"elliot": "eliot"})


def tokens(value) -> list[str]:
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    return re.findall(r"[a-z0-9]+", text)


def normalized(value) -> str:
    return " ".join(VARIANTS.get(t, t) for t in tokens(value))


def searchable(record) -> str:
    # Superseded values are available in the audit, not searchable as current facts.
    if isinstance(record, dict):
        record = {k: v for k, v in record.items() if k not in {"review_corrections", "date_provenance", "id"}}
    return normalized(json.dumps(record, ensure_ascii=False, default=str))


def matches(query: str, record) -> bool:
    text = searchable(record)
    return all(t in text for t in normalized(query).split())


def person_match(query: str, person: dict) -> str:
    name_text = " ".join([person.get("full_name", ""), *person.get("alternate_names", [])])
    q = normalized(query).split()
    names = normalized(name_text).split()
    if not q:
        return ""
    if all(t in names or (len(t) == 1 and t.isalpha() and any(n.startswith(t) for n in names)) for t in q):
        return "Name, initials or spelling variant"
    if matches(query, person):
        return "Profile text or sources"
    # Only name tokens; never fuzzy-match dates, IDs, places, or evidence.
    if all(t in names or (len(t) >= 4 and t.isalpha() and any(
            SequenceMatcher(None, t, n).ratio() >= .86 for n in names if len(n) >= 4)) for t in q):
        return "Similar name — check dates and relatives"
    return ""
