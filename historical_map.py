"""Leaflet map document backed exclusively by the normalized archive projection."""

import json
from pathlib import Path

from archive import ArchiveIndex

ASSETS = Path(__file__).parent / "static"


def build_historical_map_html(archive: ArchiveIndex, *, person_id: str = "",
                              event_id: str = "", place_id: str = "") -> str:
    payload = archive.map_payload()
    payload["initial"] = {"person": person_id, "event": event_id, "place": place_id}
    # JSON is data, never HTML or executable code. Escape even hostile </script>.
    encoded = json.dumps(payload, ensure_ascii=True).replace("<", "\\u003c").replace("&", "\\u0026")
    template = (ASSETS / "historical_map.html").read_text(encoding="utf-8")
    return (template.replace("/* LEAFLET_CSS */", (ASSETS / "vendor/leaflet/leaflet.css").read_text())
            .replace("/* ARCHIVE_CSS */", (ASSETS / "historical_map.css").read_text())
            .replace("/* LEAFLET_JS */", (ASSETS / "vendor/leaflet/leaflet.js").read_text())
            .replace("/* ARCHIVE_JS */", (ASSETS / "historical_map.js").read_text())
            .replace("ARCHIVE_JSON", encoded))

