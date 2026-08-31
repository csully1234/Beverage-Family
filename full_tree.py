"""Interactive full-family map utilities.

This module contains no Streamlit dependency so its layout and HTML generation
can be tested independently from the web UI.
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Mapping

from family_data import Record, friendly_identifier, life_span, year_from_date


NODE_WIDTH = 210
NODE_HEIGHT = 66
X_GAP = 34
Y_GAP = 78
MARGIN_X = 64
MARGIN_Y = 54


def _all_tree_ids(
    people_by_id: Mapping[str, Record],
    relationships: Mapping[str, Mapping[str, set[str]]],
) -> set[str]:
    ids = set(people_by_id)
    for mapping in relationships.values():
        for person_id, related_ids in mapping.items():
            ids.add(str(person_id))
            ids.update(str(item) for item in related_ids)
    return ids


def _generation_map(
    all_ids: set[str],
    relationships: Mapping[str, Mapping[str, set[str]]],
) -> dict[str, int]:
    parents = relationships.get("parents", {})
    memo: dict[str, int] = {}
    visiting: set[str] = set()

    def generation(person_id: str) -> int:
        if person_id in memo:
            return memo[person_id]
        if person_id in visiting:
            return 0

        visiting.add(person_id)
        known_parents = [
            str(parent_id)
            for parent_id in parents.get(person_id, set())
            if str(parent_id) in all_ids and str(parent_id) != person_id
        ]
        value = 0 if not known_parents else 1 + max(generation(parent_id) for parent_id in known_parents)
        visiting.discard(person_id)
        memo[person_id] = min(value, max(len(all_ids) - 1, 0))
        return memo[person_id]

    for person_id in sorted(all_ids):
        generation(person_id)

    # A spouse with no recorded parents is usually more useful beside their
    # partner than stranded on the root row. Align only those root-only spouses.
    spouses = relationships.get("spouses", {})
    for _ in range(2):
        changed = False
        for person_id in sorted(all_ids):
            if parents.get(person_id):
                continue
            partner_generations = [
                memo.get(str(spouse_id), 0)
                for spouse_id in spouses.get(person_id, set())
                if str(spouse_id) in all_ids
            ]
            if partner_generations:
                desired = max(partner_generations)
                if desired > memo.get(person_id, 0):
                    memo[person_id] = desired
                    changed = True
        if not changed:
            break
    return memo


def build_full_tree_model(
    people_by_id: Mapping[str, Record],
    relationships: Mapping[str, Mapping[str, set[str]]],
) -> dict[str, Any]:
    """Return positioned nodes and deduplicated edges for the whole archive."""

    all_ids = _all_tree_ids(people_by_id, relationships)
    generations = _generation_map(all_ids, relationships)
    parents = relationships.get("parents", {})

    layers: defaultdict[int, list[str]] = defaultdict(list)
    for person_id in all_ids:
        layers[generations.get(person_id, 0)].append(person_id)

    def sort_key(person_id: str) -> tuple[tuple[str, ...], int, str]:
        person = people_by_id.get(person_id, {})
        parent_key = tuple(sorted(str(item) for item in parents.get(person_id, set())))
        birth_year = year_from_date(person.get("birth_date")) or 9999
        name = str(person.get("full_name") or friendly_identifier(person_id)).casefold()
        return parent_key, birth_year, name

    max_layer_width = max(
        (
            len(person_ids) * NODE_WIDTH
            + max(len(person_ids) - 1, 0) * X_GAP
            for person_ids in layers.values()
        ),
        default=0,
    )
    canvas_width = max(1180, max_layer_width + MARGIN_X * 2)
    max_generation = max(layers, default=0)
    canvas_height = max(
        720,
        MARGIN_Y * 2 + (max_generation + 1) * NODE_HEIGHT + max_generation * Y_GAP,
    )

    nodes: list[dict[str, Any]] = []
    position_by_id: dict[str, tuple[float, float]] = {}
    for generation in sorted(layers):
        person_ids = sorted(layers[generation], key=sort_key)
        layer_width = (
            len(person_ids) * NODE_WIDTH
            + max(len(person_ids) - 1, 0) * X_GAP
        )
        start_x = (canvas_width - layer_width) / 2
        y = MARGIN_Y + generation * (NODE_HEIGHT + Y_GAP)
        for index, person_id in enumerate(person_ids):
            x = start_x + index * (NODE_WIDTH + X_GAP)
            position_by_id[person_id] = (x, y)
            person = people_by_id.get(person_id)
            nodes.append(
                {
                    "id": person_id,
                    "name": (
                        str(person.get("full_name", person_id))
                        if person
                        else friendly_identifier(person_id)
                    ),
                    "life_span": life_span(person) if person else "Unresolved profile",
                    "x": round(x, 2),
                    "y": round(y, 2),
                    "unresolved": person is None,
                }
            )

    parent_edges: set[tuple[str, str]] = set()
    for child_id, parent_ids in relationships.get("parents", {}).items():
        child_id = str(child_id)
        if child_id not in all_ids:
            continue
        for parent_id in parent_ids:
            parent_id = str(parent_id)
            if parent_id in all_ids and parent_id != child_id:
                parent_edges.add((parent_id, child_id))
    for parent_id, child_ids in relationships.get("children", {}).items():
        parent_id = str(parent_id)
        if parent_id not in all_ids:
            continue
        for child_id in child_ids:
            child_id = str(child_id)
            if child_id in all_ids and parent_id != child_id:
                parent_edges.add((parent_id, child_id))

    spouse_edges: set[tuple[str, str]] = set()
    for person_id, spouse_ids in relationships.get("spouses", {}).items():
        person_id = str(person_id)
        if person_id not in all_ids:
            continue
        for spouse_id in spouse_ids:
            spouse_id = str(spouse_id)
            if spouse_id in all_ids and spouse_id != person_id:
                spouse_edges.add(tuple(sorted((person_id, spouse_id))))

    return {
        "nodes": nodes,
        "positions": position_by_id,
        "parent_edges": [list(edge) for edge in sorted(parent_edges)],
        "spouse_edges": [list(edge) for edge in sorted(spouse_edges)],
        "width": canvas_width,
        "height": canvas_height,
        "node_width": NODE_WIDTH,
        "node_height": NODE_HEIGHT,
    }


def build_full_tree_html(
    people_by_id: Mapping[str, Record],
    relationships: Mapping[str, Mapping[str, set[str]]],
) -> str:
    """Build a self-contained, dependency-free pan/zoom SVG family map."""

    model = build_full_tree_model(people_by_id, relationships)
    payload = json.dumps(model, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --ink:#19313a; --navy:#123542; --sea:#39717d; --sky:#dcebed;
    --cream:#f7f3ea; --paper:#fffdf8; --brass:#aa7b3f; --line:#8ca1a5;
  }}
  * {{ box-sizing:border-box; }}
  html, body {{ margin:0; height:100%; background:var(--cream); color:var(--ink);
    font-family:Arial, Helvetica, sans-serif; }}
  #shell {{ height:800px; display:flex; flex-direction:column; border:1px solid rgba(25,49,58,.18);
    border-radius:16px; overflow:hidden; background:var(--paper); }}
  #toolbar {{ min-height:58px; padding:10px 12px; display:flex; gap:8px; align-items:center;
    flex-wrap:wrap; border-bottom:1px solid rgba(25,49,58,.16); background:#f7f3ea; }}
  #toolbar button, #toolbar select {{
    min-height:36px; border:1px solid rgba(18,53,66,.32); border-radius:999px;
    background:#fffdf8; color:#19313a; font-weight:700; padding:7px 12px;
  }}
  #toolbar button {{ cursor:pointer; }}
  #toolbar button:hover {{ background:#dcebed; }}
  #personSelect {{ max-width:320px; flex:1 1 220px; }}
  #status {{ margin-left:auto; font-size:12px; color:#50686f; white-space:nowrap; }}
  #viewport {{ flex:1; min-height:0; position:relative; overflow:hidden; background:
    radial-gradient(circle at 50% 10%, rgba(57,113,125,.08), transparent 30rem), #fffdf8; }}
  #tree {{ width:100%; height:100%; display:block; touch-action:none; cursor:grab; user-select:none; }}
  #tree.dragging {{ cursor:grabbing; }}
  .parent-edge {{ fill:none; stroke:#789097; stroke-width:1.5; opacity:.58; }}
  .spouse-edge {{ fill:none; stroke:#8b779a; stroke-width:1.7; stroke-dasharray:6 4; opacity:.75; }}
  .node rect {{ fill:#fffdf8; stroke:#6f969f; stroke-width:1.5; rx:11; ry:11; }}
  .node text {{ fill:#19313a; pointer-events:none; }}
  .node .name {{ font-size:13px; font-weight:700; }}
  .node .years {{ font-size:11px; fill:#52676e; }}
  .node {{ cursor:pointer; }}
  .node:hover rect, .node.selected rect {{ stroke:#aa7b3f; stroke-width:3; filter:drop-shadow(0 3px 5px rgba(18,53,66,.16)); }}
  .node.unresolved rect {{ fill:#f2eee5; stroke:#9a8f80; stroke-dasharray:5 3; }}
  .node.unresolved {{ cursor:default; }}
  #help {{ position:absolute; right:12px; bottom:10px; padding:7px 10px; border-radius:10px;
    background:rgba(255,253,248,.94); border:1px solid rgba(25,49,58,.14);
    color:#50686f; font-size:11px; pointer-events:none; }}
  @media (max-width:700px) {{
    #shell {{ height:720px; border-radius:12px; }}
    #toolbar {{ align-items:stretch; }}
    #toolbar button {{ flex:1 0 auto; }}
    #status {{ width:100%; margin-left:0; }}
    #help {{ display:none; }}
  }}
</style>
</head>
<body>
<div id="shell">
  <div id="toolbar">
    <select id="personSelect" aria-label="Find a person">
      <option value="">Find and center a person…</option>
    </select>
    <button id="fit" type="button">Fit whole tree</button>
    <button id="zoomIn" type="button" aria-label="Zoom in">＋</button>
    <button id="zoomOut" type="button" aria-label="Zoom out">−</button>
    <button id="reset" type="button">100%</button>
    <span id="status"></span>
  </div>
  <div id="viewport">
    <svg id="tree" role="img" aria-label="Interactive full Beverage family tree">
      <g id="world"></g>
    </svg>
    <div id="help">Drag to pan · wheel/pinch or +/− to zoom · click a profile to open it</div>
  </div>
</div>
<script>
const DATA = {payload};
const NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("tree");
const world = document.getElementById("world");
const select = document.getElementById("personSelect");
const status = document.getElementById("status");
const nodeById = new Map(DATA.nodes.map(n => [n.id, n]));
let scale = 1, tx = 20, ty = 20, dragging = false, dragged = false;
let startX = 0, startY = 0, startTx = 0, startTy = 0;

function make(tag, attrs={{}}) {{
  const el = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, String(value));
  return el;
}}
function applyTransform() {{
  world.setAttribute("transform", `translate(${{tx}} ${{ty}}) scale(${{scale}})`);
  status.textContent = `${{DATA.nodes.length}} people/relative nodes · ${{Math.round(scale * 100)}}%`;
}}
function clampScale(value) {{ return Math.min(4, Math.max(0.06, value)); }}
function zoomAt(factor, cx=svg.clientWidth/2, cy=svg.clientHeight/2) {{
  const worldX = (cx - tx) / scale, worldY = (cy - ty) / scale;
  const next = clampScale(scale * factor);
  tx = cx - worldX * next; ty = cy - worldY * next; scale = next; applyTransform();
}}
function fitTree() {{
  const vw = Math.max(svg.clientWidth, 320), vh = Math.max(svg.clientHeight, 320);
  scale = clampScale(Math.min((vw - 36) / DATA.width, (vh - 36) / DATA.height, 1));
  tx = (vw - DATA.width * scale) / 2;
  ty = (vh - DATA.height * scale) / 2;
  applyTransform();
}}
function resetTree() {{ scale = 1; tx = 20; ty = 20; applyTransform(); }}
function edgePath(from, to) {{
  const x1 = from.x + DATA.node_width/2, y1 = from.y + DATA.node_height;
  const x2 = to.x + DATA.node_width/2, y2 = to.y;
  const mid = (y1 + y2) / 2;
  return `M ${{x1}} ${{y1}} C ${{x1}} ${{mid}}, ${{x2}} ${{mid}}, ${{x2}} ${{y2}}`;
}}
function spousePath(a, b) {{
  const x1 = a.x + DATA.node_width/2, y1 = a.y + DATA.node_height/2;
  const x2 = b.x + DATA.node_width/2, y2 = b.y + DATA.node_height/2;
  return `M ${{x1}} ${{y1}} L ${{x2}} ${{y2}}`;
}}
for (const [parentId, childId] of DATA.parent_edges) {{
  const a=nodeById.get(parentId), b=nodeById.get(childId); if (!a || !b) continue;
  world.appendChild(make("path", {{d:edgePath(a,b), class:"parent-edge"}}));
}}
for (const [aId, bId] of DATA.spouse_edges) {{
  const a=nodeById.get(aId), b=nodeById.get(bId); if (!a || !b) continue;
  world.appendChild(make("path", {{d:spousePath(a,b), class:"spouse-edge"}}));
}}
function labelLines(name) {{
  if (name.length <= 28) return [name];
  const words=name.split(/\\s+/); let first="", second="";
  for (const word of words) {{
    if (!second && (first + " " + word).trim().length <= 27) first=(first+" "+word).trim();
    else second=(second+" "+word).trim();
  }}
  return [first || name.slice(0,27), second || ""].filter(Boolean).slice(0,2);
}}
for (const node of DATA.nodes) {{
  const g=make("g", {{class:`node${{node.unresolved ? " unresolved" : ""}}`, "data-id":node.id}});
  g.setAttribute("transform", `translate(${{node.x}} ${{node.y}})`);
  g.appendChild(make("rect", {{width:DATA.node_width, height:DATA.node_height}}));
  const lines=labelLines(node.name);
  const text=make("text", {{x:DATA.node_width/2, y:lines.length > 1 ? 19 : 24, "text-anchor":"middle", class:"name"}});
  lines.forEach((line, index) => {{
    const tspan=make("tspan", {{x:DATA.node_width/2, dy:index===0 ? 0 : 15}});
    tspan.textContent=line; text.appendChild(tspan);
  }});
  g.appendChild(text);
  const years=make("text", {{x:DATA.node_width/2, y:56, "text-anchor":"middle", class:"years"}});
  years.textContent=node.life_span; g.appendChild(years);
  if (!node.unresolved) {{
    g.addEventListener("click", () => {{
      if (dragged) return;
      const target = `${{window.parent.location.pathname}}?page=people&profile=${{encodeURIComponent(node.id)}}`;
      window.parent.location.assign(target);
    }});
  }}
  world.appendChild(g);
}}
const sortedNodes=[...DATA.nodes].sort((a,b)=>a.name.localeCompare(b.name));
for (const node of sortedNodes) {{
  const option=document.createElement("option"); option.value=node.id;
  option.textContent=`${{node.name}} · ${{node.life_span}}`;
  select.appendChild(option);
}}
function focusNode(id) {{
  document.querySelectorAll(".node.selected").forEach(el=>el.classList.remove("selected"));
  const node=nodeById.get(id); if (!node) return;
  scale=Math.max(scale, 0.95);
  tx=svg.clientWidth/2-(node.x+DATA.node_width/2)*scale;
  ty=svg.clientHeight/2-(node.y+DATA.node_height/2)*scale;
  const el=world.querySelector(`[data-id="${{CSS.escape(id)}}"]`);
  if (el) el.classList.add("selected");
  applyTransform();
}}
select.addEventListener("change", () => {{ if (select.value) focusNode(select.value); }});
document.getElementById("fit").addEventListener("click", fitTree);
document.getElementById("zoomIn").addEventListener("click", () => zoomAt(1.25));
document.getElementById("zoomOut").addEventListener("click", () => zoomAt(0.8));
document.getElementById("reset").addEventListener("click", resetTree);
svg.addEventListener("wheel", event => {{
  event.preventDefault();
  const rect=svg.getBoundingClientRect();
  zoomAt(event.deltaY < 0 ? 1.12 : 0.89, event.clientX-rect.left, event.clientY-rect.top);
}}, {{passive:false}});
svg.addEventListener("pointerdown", event => {{
  dragging=true; dragged=false; startX=event.clientX; startY=event.clientY; startTx=tx; startTy=ty;
  svg.setPointerCapture(event.pointerId); svg.classList.add("dragging");
}});
svg.addEventListener("pointermove", event => {{
  if (!dragging) return;
  const dx=event.clientX-startX, dy=event.clientY-startY;
  if (Math.abs(dx)+Math.abs(dy) > 4) dragged=true;
  tx=startTx+dx; ty=startTy+dy; applyTransform();
}});
function endDrag() {{ dragging=false; svg.classList.remove("dragging"); setTimeout(()=>{{dragged=false;}},0); }}
svg.addEventListener("pointerup", endDrag);
svg.addEventListener("pointercancel", endDrag);
window.addEventListener("resize", fitTree);
requestAnimationFrame(fitTree);
</script>
</body>
</html>"""
