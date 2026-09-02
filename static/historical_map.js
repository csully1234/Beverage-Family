/* The pure predicates are also exercised under Node by the regression suite. */
function connectionOverlaps(link, start, end, includeUndated) {
  const first = link.date_from ? Number(link.date_from.slice(0, 4)) : null;
  const last = link.date_to ? Number(link.date_to.slice(0, 4)) : null;
  if (first === null && last === null) return includeUndated;
  return (first === null || first <= end) && (last === null || last >= start);
}

function matchingLinks(data, filters) {
  const eligible = data.links.filter(link =>
    (!filters.category || link.category === filters.category) &&
    connectionOverlaps(link, filters.start, filters.end, filters.undated));
  const relatedAssertion = (a, b) => a.place_id === b.place_id && a.source_ids.some(s => b.source_ids.includes(s));
  if (filters.person) {
    const direct = eligible.filter(l => l.subject_type === "person" && l.subject_id === filters.person);
    const eventIds = new Set(data.events.filter(e => e.people_ids.includes(filters.person)).map(e => e.id));
    return eligible.filter(l => direct.includes(l) || (l.subject_type === "event" && eventIds.has(l.subject_id) && direct.some(p => relatedAssertion(l,p))));
  }
  if (filters.event) {
    const direct = eligible.filter(l => l.subject_type === "event" && l.subject_id === filters.event);
    const participants = new Set(data.events.find(e => e.id === filters.event)?.people_ids || []);
    return eligible.filter(l => direct.includes(l) || (l.subject_type === "person" && participants.has(l.subject_id) && direct.some(e => relatedAssertion(l,e))));
  }
  return eligible;
}

if (typeof module !== "undefined") module.exports = {connectionOverlaps, matchingLinks};

if (typeof document !== "undefined") (() => {
  "use strict";
  const DATA = JSON.parse(document.getElementById("archive-data").textContent);
  const byId = records => new Map(records.map(record => [record.id, record]));
  const places = byId(DATA.places), people = byId(DATA.people), events = byId(DATA.events), sources = byId(DATA.sources);
  const $ = id => document.getElementById(id);
  const friendly = value => value.replaceAll("_", " ");
  const years = DATA.links.flatMap(l => [l.date_from, l.date_to]).filter(Boolean).map(v => Number(v.slice(0, 4)));
  const earliest = years.length ? Math.min(...years) : 1700, latest = years.length ? Math.max(...years) : new Date().getFullYear();
  let selected = "", visible = [], filtered = [], markers = new Map(), map = null;
  // Use the embedding app URL as the base for stable profile/archive links.
  // No query parameters or family data are sent to the map tile provider.
  const appBase = /^https?:/.test(document.referrer) ? document.referrer : document.baseURI;
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function anchor(text, url) {
    const node = element("a", text);
    const resolved = new URL(url, appBase);
    if (!["http:", "https:"].includes(resolved.protocol)) return element("span", text);
    node.href = resolved.href; node.target = "_blank"; node.rel = "noopener noreferrer";
    return node;
  }
  function options(id, records, label) {
    for (const record of records) {
      const option = element("option", label(record)); option.value = record.id; $(id).append(option);
    }
  }
  options("person", [...DATA.people].sort((a, b) => a.name.localeCompare(b.name)), p => p.name);
  options("event", [...DATA.events].sort((a, b) => (a.year || 9999) - (b.year || 9999)), e => `${e.date} · ${e.title}`);
  options("category", [...new Set(DATA.links.map(l => l.category))].sort().map(id => ({id})), c => friendly(c.id));
  $("from").value = earliest; $("to").value = latest;
  const palette = {municipality:"#39717d", harbor:"#2066b1", cemetery:"#66644a", country:"#755193", region:"#755193"};
  const warning = message => { $("map-warning").hidden = false; $("map-warning").textContent = message; };
  if (typeof L !== "undefined") {
    map = L.map("map", {scrollWheelZoom:false}).setView([44.13, -68.92], 10);
    L.control.scale({imperial:true, metric:true}).addTo(map);
    const tiles = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom:19, referrerPolicy:"origin", attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>'
    }).addTo(map);
    tiles.on("tileerror", () => warning("The background map could not load. Place markers, filters, and the list remain available; check your connection to OpenStreetMap."));
  } else {
    warning("The interactive map could not start. You can still explore every place using the list below.");
  }
  function fitResults() {
    const points = visible.filter(p => p.latitude !== null && p.longitude !== null).map(p => [p.latitude, p.longitude]);
    if (!map || !points.length) return;
    const only = visible.length === 1 ? visible[0] : null;
    const maxZoom = only?.coordinate_precision === "country" ? 5 : only?.coordinate_precision === "municipality" ? 11 : 13;
    map.fitBounds(points, {padding:[35, 35], maxZoom});
  }
  function linkSources(parent, ids) {
    const row = element("div", undefined, "citation");
    row.append(element("span", "Evidence: "));
    for (const sid of [...new Set(ids)]) {
      const s = sources.get(sid); if (s) row.append(anchor(s.title, s.url));
    }
    parent.append(row);
  }
  function describeLinks(kind, links, parent) {
    parent.append(element("h3", kind === "person" ? "Connected people" : "Historical events"));
    const assertions = links.filter(l => l.subject_type === kind);
    if (!assertions.length) parent.append(element("p", "No links in this selection.", "metadata"));
    for (const link of assertions) {
      const subject = (kind === "person" ? people : events).get(link.subject_id);
      if (!subject) continue;
      const card = element("div", undefined, "assertion");
      card.append(anchor(subject.name || subject.title, subject.url));
      card.append(element("p", `${friendly(link.relation)} · ${link.date_from || "date unknown"}${link.date_to && link.date_to !== link.date_from ? " – " + link.date_to : ""}${link.date_precision === "approximate" ? " (approximate)" : ""}`, "metadata"));
      card.append(element("p", link.summary));
      card.append(element("span", friendly(link.evidence_level), "evidence"));
      linkSources(card, link.source_ids); parent.append(card);
    }
  }
  function detail(id) {
    selected = id; const place = places.get(id); if (!place) return;
    const box = $("detail"); box.replaceChildren();
    box.append(element("h2", place.name));
    box.append(element("p", `${friendly(place.type)} · ${friendly(place.coordinate_precision)} point · ${place.confidence} location confidence`, "metadata"));
    if (place.alternate_names.length) box.append(element("p", "Also recorded as: " + place.alternate_names.join("; "), "metadata"));
    box.append(element("p", place.historical_notes));
    box.append(element("p", place.coordinate_notes, "metadata"));
    const actions = element("div", undefined, "detail-actions");
    actions.append(anchor("Open place record", `?page=places&place=${encodeURIComponent(id)}`));
    if (place.parent_place_id && places.has(place.parent_place_id)) {
      actions.append(anchor(`Within ${places.get(place.parent_place_id).name}`, `?page=places&place=${encodeURIComponent(place.parent_place_id)}`));
    }
    box.append(actions);
    const here = filtered.filter(l => l.place_id === id);
    describeLinks("person", here, box); describeLinks("event", here, box);
    if ($("person").value || $("event").value || $("category").value || Number($("from").value) !== earliest || Number($("to").value) !== latest || !$("undated").checked) {
      box.append(element("p", "Showing connections matching your filters. The place record includes all reviewed links.", "metadata"));
    }
    box.append(element("h3", "Place references")); linkSources(box, place.sources);
    for (const [pid, marker] of markers) {
      const node = marker.getElement();
      if (node) { node.style.backgroundColor = pid === id ? "#ad671a" : (palette[places.get(pid).type] || "#39717d"); node.setAttribute("aria-pressed", String(pid === id)); }
    }
    for (const button of $("place-list").querySelectorAll("button")) button.setAttribute("aria-pressed", String(button.dataset.place === id));
  }
  function update(fit = false) {
    const start = Number($("from").value), end = Number($("to").value);
    if (!$("from").value || !$("to").value || !Number.isInteger(start) || !Number.isInteger(end) || start < 1 || end > 9999 || start > end) {
      $("status").textContent = "Enter a valid year range (from year must be no later than through year)."; return;
    }
    filtered = matchingLinks(DATA, {person:$("person").value, event:$("event").value,
      category:$("category").value, start, end, undated:$("undated").checked});
    const ids = new Set(filtered.map(l => l.place_id));
    // Places without assertions are still browsable in the unfiltered archive.
    const unfiltered = !$("person").value && !$("event").value && !$("category").value && start === earliest && end === latest && $("undated").checked;
    visible = DATA.places.filter(p => ids.has(p.id) || unfiltered).sort((a,b) => a.name.localeCompare(b.name));
    if (map) for (const marker of markers.values()) map.removeLayer(marker);
    markers = new Map(); $("place-list").replaceChildren();
    for (const p of visible) {
      const button = element("button", p.name); button.type = "button"; button.dataset.place = p.id;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => { detail(p.id); if (map && p.latitude !== null) map.setView([p.latitude,p.longitude], p.coordinate_precision === "country" ? 5 : p.coordinate_precision === "municipality" ? 11 : 13); });
      $("place-list").append(button);
      if (map && p.latitude !== null && p.longitude !== null) {
        const icon = L.divIcon({className:"archive-pin", iconSize:[18,18], iconAnchor:[9,9]});
        const marker = L.marker([p.latitude,p.longitude], {icon, title:p.name, alt:p.name, keyboard:true}).addTo(map);
        marker.bindTooltip(element("span",p.name)); marker.on("click", () => detail(p.id));
        markers.set(p.id, marker); marker.getElement().style.backgroundColor = palette[p.type] || "#39717d";
      }
    }
    $("status").textContent = `${visible.length} places · ${filtered.length} documented connections${$("person").value ? " for " + people.get($("person").value).name : ""}`;
    if (!visible.length) {
      $("detail").replaceChildren(element("h2", "No matching places"), element("p", "Try widening the years, including undated connections, or resetting the filters.")); selected = "";
    } else if (visible.some(p => p.id === selected)) detail(selected);
    else { selected = ""; $("detail").replaceChildren(element("h2", "Explore a place"), element("p", "Choose a pin or a place below the map to inspect its evidence.")); }
    if (fit) fitResults();
  }
  function reset() {
    for (const id of ["person","event","category"]) $(id).value = "";
    $("from").value = earliest; $("to").value = latest; $("undated").checked = true;
  }
  $("filters").addEventListener("submit", e => { e.preventDefault(); update(); });
  for (const id of ["category","from","to","undated"]) $(id).addEventListener("change", () => update(true));
  $("person").addEventListener("change", () => { $("event").value = ""; update(true); });
  $("event").addEventListener("change", () => {
    // A jump is a navigation action: reveal the selected event even when old filters conflict.
    const eid = $("event").value; reset(); $("event").value = eid; update(true);
    if (visible.length) detail(visible[0].id);
  });
  $("reset").addEventListener("click", () => { reset(); update(); });
  $("fit").addEventListener("click", fitResults);
  $("bay").addEventListener("click", () => { if (map) map.setView([44.13,-68.92],10); });
  if (people.has(DATA.initial.person)) $("person").value = DATA.initial.person;
  if (events.has(DATA.initial.event)) { $("person").value = ""; $("event").value = DATA.initial.event; }
  if (places.has(DATA.initial.place)) selected = DATA.initial.place;
  update(Boolean($("person").value || $("event").value));
  if (selected && map) {
    const p = places.get(selected);
    if (p.latitude !== null) map.setView([p.latitude,p.longitude], p.coordinate_precision === "country" ? 5 : p.coordinate_precision === "municipality" ? 11 : 13);
  } else if (DATA.initial.event && visible.length) detail(visible[0].id);
})();
