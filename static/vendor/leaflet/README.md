# Leaflet 1.9.4

Vendored from the official distribution linked by https://leafletjs.com/download.html.
The BSD-2-Clause license is included in `LICENSE`.

Verified SHA-256 (base64), as published on the Leaflet download page:

- `leaflet.js`: `20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=`
- `leaflet.css`: `p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=`

The Python renderer embeds both assets into the map document. There are no CDN
script/style requests in production. Default marker/layer-selector images are
unused: the map uses `L.divIcon` and no raster layer selector. Preserve upstream
bytes when updating so these hashes remain independently verifiable.
