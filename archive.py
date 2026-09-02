"""Normalized historical archive queries, independent of Streamlit and maps.

Legacy genealogy and inline citations are never rewritten. Reviewed place
assertions reference their subject and evidence by stable ID; inverse indexes
are computed once, without inferring attendance, residence, or travel.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Mapping
from urllib.parse import urlencode, urlsplit

from family_data import Record, date_sort_key, format_date, year_from_date


ARCHIVE_FILES = {
    "archive_sources": "archive_sources.json",
    "places": "places.json",
    "place_links": "place_links.json",
}
PUBLIC_EVIDENCE = {"verified", "strongly_supported", "corroboration"}


def safe_url(value: Any) -> bool:
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"https", "http"} and bool(parsed.hostname) and not (
            parsed.username or parsed.password
        )
    except ValueError:
        return False


def historical_person(person: Mapping[str, Any], today: date | None = None) -> bool:
    """Fail closed for possibly living people; never use residence text."""
    today = today or date.today()
    if person.get("living") is True or person.get("is_living") is True:
        return False
    death = year_from_date(person.get("death_date"))
    birth = year_from_date(person.get("birth_date"))
    return bool((death and death <= today.year) or (birth and birth <= today.year - 120))


def archive_url(page: str, **params: str) -> str:
    return "?" + urlencode({"page": page, **params})


def link_overlaps(link: Mapping[str, Any], start: int, end: int,
                  include_undated: bool = True) -> bool:
    """Inclusive year overlap. Null endpoints are open; two nulls are undated.

    These are dates of a documented connection, never an inferred lifetime or
    the publication date of an obituary. Year/approximate dates stay coarse.
    """
    first = year_from_date(link.get("date_from"))
    last = year_from_date(link.get("date_to"))
    if first is None and last is None:
        return include_undated
    return (first is None or first <= end) and (last is None or last >= start)


class ArchiveIndex:
    def __init__(self, data: Mapping[str, list[Record]]):
        self.people = {p["id"]: p for p in data["people"]}
        self.events = {e["id"]: e for e in data["events"]}
        self.places = {p["id"]: p for p in data.get("places", [])}
        self.sources = {s["id"]: s for s in data.get("archive_sources", [])}
        self.links = list(data.get("place_links", []))
        self.by_place: dict[str, list[Record]] = defaultdict(list)
        self.by_subject: dict[tuple[str, str], list[Record]] = defaultdict(list)
        self.source_refs: dict[tuple[str, str], set[str]] = defaultdict(set)
        for source in self.sources.values():
            for kind, field in (("person", "people_ids"), ("event", "event_ids"), ("place", "place_ids")):
                for identifier in source.get(field, []):
                    self.source_refs[kind, identifier].add(source["id"])
        for place in self.places.values():
            self.source_refs["place", place["id"]].update(place.get("sources", []))
        for link in self.links:
            self.by_place[link["place_id"]].append(link)
            self.by_subject[link["subject_type"], link["subject_id"]].append(link)
            self.source_refs[link["subject_type"], link["subject_id"]].update(link["source_ids"])
            self.source_refs["place", link["place_id"]].update(link["source_ids"])

    def sources_for(self, kind: str, identifier: str) -> list[Record]:
        return sorted((self.sources[sid] for sid in self.source_refs[kind, identifier]
                       if sid in self.sources), key=lambda s: (s["title"], s["id"]))

    def places_for(self, kind: str, identifier: str) -> list[Record]:
        ids = {link["place_id"] for link in self.by_subject[kind, identifier]}
        return sorted((self.places[pid] for pid in ids if pid in self.places), key=lambda p: p["name"])

    def related(self, place_id: str) -> dict[str, list[Record]]:
        links = self.by_place[place_id]
        people_ids = {l["subject_id"] for l in links if l["subject_type"] == "person"}
        event_ids = {l["subject_id"] for l in links if l["subject_type"] == "event"}
        return {
            "people": sorted((self.people[i] for i in people_ids), key=lambda p: p["full_name"]),
            "events": sorted((self.events[i] for i in event_ids), key=date_sort_key),
            "sources": self.sources_for("place", place_id),
            "links": links,
        }

    def map_payload(self) -> dict[str, Any]:
        """Explicit public projection: no raw profiles, residences, or addresses.

        Validation is the editing gate. This second boundary also omits a
        possibly living participant if an unvalidated file reaches runtime.
        """
        safe_people = {pid for pid, p in self.people.items() if historical_person(p)}
        public_places = {pid: p for pid, p in self.places.items() if p.get("public") is True}
        safe_events = {eid for eid, event in self.events.items()
                       if all(pid in safe_people for pid in event.get("people_involved", []))}
        links = [l for l in self.links if l["place_id"] in public_places
                 and l["evidence_level"] in PUBLIC_EVIDENCE
                 and l["subject_id"] in (safe_people if l["subject_type"] == "person" else safe_events)]
        people_ids = {l["subject_id"] for l in links if l["subject_type"] == "person"}
        event_ids = {l["subject_id"] for l in links if l["subject_type"] == "event"}
        source_ids = {sid for l in links for sid in l["source_ids"]}
        source_ids.update(sid for p in public_places.values() for sid in p.get("sources", []))
        people = [{"id": pid, "name": self.people[pid]["full_name"],
                   "url": archive_url("people", profile=pid)} for pid in sorted(people_ids)]
        events = [{"id": eid, "title": self.events[eid]["title"],
                   "people_ids": self.events[eid].get("people_involved", []),
                   "date": format_date(self.events[eid].get("date"), self.events[eid].get("date_precision")),
                   "year": year_from_date(self.events[eid].get("date")),
                   "url": archive_url("timeline", event=eid)} for eid in sorted(event_ids)]
        sources = [{"id": sid, "title": self.sources[sid]["short_title"],
                    "url": archive_url("archive", source=sid)} for sid in sorted(source_ids)]
        return {"places": list(public_places.values()), "links": links,
                "people": people, "events": events, "sources": sources}
