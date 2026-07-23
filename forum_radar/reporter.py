from datetime import datetime
from pathlib import Path
import json


def build_report(config, db, recent_scans: list, courses: list, stats: dict) -> str:
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    cat_groups = {}
    for group_name, group_info in config.CATEGORY_GROUPS.items():
        for cat in group_info["categories"]:
            cat_groups[cat] = {"group": group_name, "icon": group_info["icon"]}

    courses_json = _courses_to_json(courses, cat_groups)
    scans_json = json.dumps(recent_scans)
    cat_groups_json = json.dumps(cat_groups)
    group_defs_json = json.dumps(
        {k: {"icon": v["icon"], "categories": v["categories"]}
         for k, v in config.CATEGORY_GROUPS.items()}
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Forum Radar — Course Database</title>
{STYLES}
</head>
<body>

<div id="app">
  <header>
    <h1>📡 Forum Radar</h1>
    <p class="meta">Last scan: {now} — <a href="{config.FORUM_URL}" target="_blank">Internet Marketing Special Downloads</a></p>
    <div class="stats-bar">
      <div class="stat"><span class="num" id="stat-total">{stats["active"]}</span><span class="lbl">active</span></div>
      <div class="stat"><span class="num" id="stat-dl">{stats["downloads"]}</span><span class="lbl">recommended</span></div>
      <div class="stat"><span class="num" id="stat-high">{stats["high_value"]}</span><span class="lbl">high value</span></div>
      <div class="stat"><span class="num">{stats["total"]}</span><span class="lbl">all time</span></div>
    </div>
  </header>

  <div class="toolbar">
    <input id="globalSearch" type="text" placeholder="Search title, creator, description..." oninput="filterTable()">
    <button id="wrapToggle" class="btn btn-sm btn-outline" onclick="toggleWrap()" title="Toggle text wrapping">Wrap</button>
    <button class="btn btn-sm btn-outline" onclick="resetDismissed()">Show hidden ({dismissed_count(config, db)})</button>
  </div>

  <div class="cat-filters" id="catFilters"></div>

  <div class="table-wrap">
    <table id="courseTable">
      <thead>
        <tr>
          <th data-col="date_detected" onclick="sortBy(this)" class="col-date">Added</th>
          <th data-col="title" onclick="sortBy(this)" class="col-title">Course</th>
          <th data-col="course_creator" onclick="sortBy(this)" class="col-creator">Creator</th>
          <th data-col="project_label" onclick="sortBy(this)" class="col-cat">Category</th>
          <th data-col="advertised_price" onclick="sortBy(this)" class="col-price num">Forum Price</th>
          <th data-col="online_price" onclick="sortBy(this)" class="col-online num">Online Price</th>
          <th class="col-desc">What You Get</th>
          <th data-col="value_score" onclick="sortBy(this)" class="col-score num">Score</th>
          <th class="col-actions">Act</th>
        </tr>
      </thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>

  <div id="detailPanel" class="detail-panel hidden">
    <div class="detail-header">
      <h3 id="detailTitle"></h3>
      <button class="btn btn-sm btn-outline" onclick="closeDetail()">✕</button>
    </div>
    <div class="detail-body" id="detailBody"></div>
  </div>
</div>

<div id="scanLog" class="scan-log">
  <h4>Scan History</h4>
  <ul id="scanList"></ul>
</div>

<script>
const COURSES = {courses_json};
const SCANS = {scans_json};
const CAT_GROUPS = {cat_groups_json};
const GROUP_DEFS = {group_defs_json};
let dismissedIds = new Set(JSON.parse(localStorage.getItem('fr_dismissed') || '[]'));
let sortCol = 'value_score';
let sortAsc = false;
let wrapMode = false;
let activeCats = new Set();

function fmtDate(d) {{
  if (!d) return '';
  const dt = new Date(d);
  if (isNaN(dt)) return d;
  return dt.toLocaleDateString('en-US', {{month:'short', day:'numeric'}});
}}

function fmtPrice(p) {{
  if (!p || p === 0 || p === '0') return '—';
  return '$' + String(p).replace(/^\\$/, '');
}}

function truncate(s, n) {{
  if (!s) return '';
  return s.length > n ? s.slice(0, n) + '…' : s;
}}

function getTag(label, cls) {{
  return `<span class="tag tag-${{cls}}">${{label}}</span>`;
}}

function renderCatFilters() {{
  const container = document.getElementById('catFilters');
  let html = '';
  for (const [group, info] of Object.entries(GROUP_DEFS)) {{
    html += `<div class="cat-group"><span class="cat-group-label">${{info.icon}} ${{group}}</span>`;
    for (const cat of info.categories) {{
      const active = activeCats.size === 0 || activeCats.has(cat) ? 'active' : '';
      html += `<button class="cat-btn ${{active}}" data-cat="${{cat}}" onclick="toggleCat('${{cat}}')">${{cat}}</button>`;
    }}
    html += '</div>';
  }}
  html += '<div style="margin-top:4px"><button class="cat-btn cat-btn-clear" onclick="clearCats()">Clear filters</button></div>';
  container.innerHTML = html;
}}

function toggleCat(cat) {{
  if (activeCats.has(cat)) activeCats.delete(cat);
  else activeCats.add(cat);
  renderCatFilters();
  filterTable();
}}

function clearCats() {{
  activeCats.clear();
  renderCatFilters();
  filterTable();
}}

function toggleWrap() {{
  wrapMode = !wrapMode;
  document.getElementById('courseTable').classList.toggle('wrap', wrapMode);
  document.getElementById('wrapToggle').classList.toggle('active', wrapMode);
}}

function makeResizable() {{
  document.querySelectorAll('th').forEach(th => {{
    const grip = document.createElement('div');
    grip.className = 'resize-grip';
    th.appendChild(grip);
    let startX, startW;
    grip.addEventListener('mousedown', e => {{
      e.preventDefault();
      e.stopPropagation();
      startX = e.clientX;
      startW = th.offsetWidth;
      document.addEventListener('mousemove', doResize);
      document.addEventListener('mouseup', stopResize);
      document.body.style.cursor = 'col-resize';
    }});
    function doResize(e) {{
      const w = Math.max(40, startW + (e.clientX - startX));
      th.style.width = w + 'px';
      const colIdx = Array.from(th.parentElement.children).indexOf(th);
      document.querySelectorAll('#courseTable tbody tr').forEach(tr => {{
        const td = tr.children[colIdx];
        if (td) td.style.width = w + 'px';
      }});
    }}
    function stopResize() {{
      document.removeEventListener('mousemove', doResize);
      document.removeEventListener('mouseup', stopResize);
      document.body.style.cursor = '';
    }}
  }});
}}

function renderTable() {{
  const tbody = document.getElementById('tableBody');
  const search = document.getElementById('globalSearch').value.toLowerCase();

  let filtered = COURSES.filter(c => {{
    if (dismissedIds.has(String(c.thread_id))) return false;
    if (activeCats.size > 0 && !activeCats.has(c.project_label)) return false;
    if (search) {{
      const text = (c.title + ' ' + (c.course_creator||'') + ' ' + (c.description||'') + ' ' + (c.description_bullets||'')).toLowerCase();
      if (!text.includes(search)) return false;
    }}
    return true;
  }});

  filtered.sort((a, b) => {{
    let va = a[sortCol], vb = b[sortCol];
    if (['value_score', 'popularity_score', 'advertised_price', 'views', 'replies'].includes(sortCol)) {{
      va = Number(va) || 0; vb = Number(vb) || 0;
      return sortAsc ? va - vb : vb - va;
    }}
    va = String(va || '').toLowerCase();
    vb = String(vb || '').toLowerCase();
    return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
  }});

  tbody.innerHTML = filtered.map(c => {{
    const recCls = c.recommendation || 'skip';
    const priceDisplay = fmtPrice(c.advertised_price);
    const onlineDisplay = c.online_price_url
      ? `<a href="${{c.online_price_url}}" target="_blank" onclick="event.stopPropagation()">${{fmtPrice(c.online_price)}}</a>`
      : fmtPrice(c.online_price);
    const descBullets = c.description_bullets
      ? c.description_bullets.split('\\n').slice(0, 4).map(b => `<li>${{truncate(b, 120)}}</li>`).join('')
      : '';
    const descHtml = descBullets
      ? `<ul class="bullets">${{descBullets}}</ul>`
      : `<span class="desc-text">${{truncate(c.description || '', 150)}}</span>`;

    return `<tr onclick="openDetail(${{c.thread_id}})">
      <td class="col-date">${{fmtDate(c.date_detected)}}</td>
      <td class="col-title"><a href="${{c.url}}" target="_blank" onclick="event.stopPropagation()">${{c.title}}</a></td>
      <td class="col-creator"><strong>${{c.course_creator || c.uploader || '—'}}</strong></td>
      <td class="col-cat">${{c.project_label ? getTag(c.project_label, 'project') : ''}}</td>
      <td class="col-price num">${{priceDisplay}}</td>
      <td class="col-online num">${{onlineDisplay}}</td>
      <td class="col-desc">${{descHtml}}</td>
      <td class="col-score num">
        <span class="score-bar"><span style="width:${{Math.min((c.value_score||0)/1.2, 100)}}%"></span></span>
        ${{c.value_score || 0}}
      </td>
      <td class="col-actions" onclick="event.stopPropagation()">
        <button class="btn btn-sm btn-outline" onclick="dismiss(${{c.thread_id}})" title="Dismiss">✕</button>
      </td>
    </tr>`;
  }}).join('');

  if (filtered.length === 0) {{
    tbody.innerHTML = '<tr><td colspan="9" class="empty-msg">No courses match your filters</td></tr>';
  }}

  document.getElementById('stat-total').textContent = filtered.length;
  document.getElementById('stat-dl').textContent = filtered.filter(c => c.recommendation === 'download').length;
  document.getElementById('stat-high').textContent = filtered.filter(c => c.value_tier === 'high').length;
}}

function openDetail(tid) {{
  const c = COURSES.find(x => x.thread_id === tid);
  if (!c) return;
  const panel = document.getElementById('detailPanel');
  document.getElementById('detailTitle').innerHTML = `<a href="${{c.url}}" target="_blank">${{c.title}}</a>`;

  const price = fmtPrice(c.advertised_price);
  const onlinePrice = c.online_price_url
    ? `<a href="${{c.online_price_url}}" target="_blank">${{fmtPrice(c.online_price)}}</a>`
    : fmtPrice(c.online_price);
  const bullets = c.description_bullets
    ? c.description_bullets.split('\\n').map(b => `<li>${{b}}</li>`).join('')
    : '<li>No breakdown available</li>';

  let html = `
    <div class="detail-grid">
      <div><strong>Creator</strong><br>${{c.course_creator || c.uploader || '—'}}</div>
      <div><strong>Uploaded by</strong><br>${{c.uploader || '—'}} <span class="sub-meta">${{c.uploader_group || ''}} · ${{c.uploader_posts || 0}} posts</span></div>
      <div><strong>Category</strong><br>${{c.project_label || 'Uncategorized'}}</div>
      <div><strong>Forum Value</strong><br>${{price || 'Not listed'}}</div>
      <div><strong>Online Price</strong><br>${{onlinePrice || 'NA'}}</div>
      <div><strong>First Seen</strong><br>${{fmtDate(c.first_seen_date) || 'Unknown'}}</div>
      <div><strong>Score</strong><br>${{c.value_score || 0}} · ${{getTag(c.value_tier || 'unscored', c.value_tier || 'unscored')}}</div>
      <div><strong>Popularity</strong><br>${{c.popularity_score || 0}}/80 · ${{c.views || 0}} views · ${{c.replies || 0}} replies</div>
      <div><strong>Size</strong><br>${{c.size || '—'}}</div>
    </div>
    <div class="detail-section">
      <strong>What You Get</strong>
      <ul class="bullets">${{bullets}}</ul>
    </div>
    ${{c.description ? '<div class="detail-section"><strong>Full Description</strong><p>' + c.description.slice(0, 600) + '</p></div>' : ''}}
    ${{c.edge_notes ? '<div class="detail-section"><strong>Edge</strong><p>' + c.edge_notes + '</p></div>' : ''}}
    ${{c.homepage_url ? '<div class="detail-section"><strong>Homepage</strong><p><a href="' + c.homepage_url + '" target="_blank">' + c.homepage_url + '</a></p></div>' : ''}}
    ${{c.download_links ? '<div class="detail-section"><strong>Download Links</strong><pre>' + c.download_links.slice(0, 600) + '</pre></div>' : ''}}
    <div class="detail-actions">
      <button class="btn btn-sm" onclick="dismiss(${{c.thread_id}}); closeDetail()">Dismiss</button>
      <a href="${{c.url}}" class="btn btn-sm" target="_blank">Open Thread</a>
    </div>
  `;
  document.getElementById('detailBody').innerHTML = html;
  panel.classList.remove('hidden');
  panel.scrollIntoView({{behavior: 'smooth', block: 'start'}});
}}

function closeDetail() {{
  document.getElementById('detailPanel').classList.add('hidden');
}}

function dismiss(tid) {{
  dismissedIds.add(String(tid));
  localStorage.setItem('fr_dismissed', JSON.stringify([...dismissedIds]));
  renderTable();
}}

function resetDismissed() {{
  if (dismissedIds.size === 0) return;
  if (!confirm('Show all hidden courses again?')) return;
  dismissedIds.clear();
  localStorage.removeItem('fr_dismissed');
  renderTable();
}}

function filterTable() {{ renderTable(); }}

function sortBy(th) {{
  const col = th.dataset.col;
  if (sortCol === col) sortAsc = !sortAsc;
  else {{ sortCol = col; sortAsc = false; }}
  document.querySelectorAll('th').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
  th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
  renderTable();
}}

function renderScans() {{
  const list = document.getElementById('scanList');
  list.innerHTML = SCANS.map(s =>
    `<li>${{new Date(s.scan_date).toLocaleString()}} — ${{s.pages_scanned}} pages, ${{s.threads_found}} threads, ${{s.new_threads}} new</li>`
  ).join('');
}}

renderCatFilters();
renderTable();
renderScans();
makeResizable();
</script>

</body>
</html>"""


def _courses_to_json(courses: list, cat_groups: dict = None) -> str:
    clean = []
    for c in courses:
        clean.append({
            "thread_id": c.get("thread_id"),
            "title": c.get("title", ""),
            "url": c.get("url", ""),
            "course_creator": c.get("course_creator", ""),
            "uploader": c.get("uploader", ""),
            "uploader_group": c.get("uploader_group", ""),
            "uploader_posts": c.get("uploader_posts", 0),
            "project_label": c.get("project_label", ""),
            "advertised_price": c.get("advertised_price", 0),
            "online_price": c.get("online_price", "NA"),
            "online_price_url": c.get("online_price_url", ""),
            "date_detected": c.get("date_detected", ""),
            "first_seen_date": c.get("first_seen_date", ""),
            "description": (c.get("description") or "")[:500],
            "description_bullets": c.get("description_bullets", ""),
            "value_tier": c.get("value_tier", "unscored"),
            "value_score": c.get("value_score", 0),
            "popularity_score": c.get("popularity_score", 0),
            "views": c.get("views", 0),
            "replies": c.get("replies", 0),
            "edge_notes": c.get("edge_notes", ""),
            "recommendation": c.get("recommendation", "skip"),
            "homepage_url": c.get("homepage_url", ""),
            "download_links": (c.get("download_links") or "")[:600],
            "size": c.get("size", ""),
        })
    return json.dumps(clean)


def dismissed_count(config, db) -> int:
    try:
        stored = db.conn.execute(
            "SELECT value FROM scan_log WHERE id=-1"
        ).fetchone()
    except Exception:
        pass
    return 0


def write_report(report_html: str, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(report_html, encoding="utf-8")
    return path


STYLES = """
<style>
  *, *::before, *::after { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', system-ui, sans-serif;
         max-width: 1440px; margin: 0 auto; padding: 20px; background: #f5f5f7; color: #1d1d1f; font-size: 13px; }
  header { margin-bottom: 16px; }
  h1 { font-size: 1.6em; margin: 0 0 2px; font-weight: 600; letter-spacing: -0.02em; }
  .meta { color: #888; font-size: 0.85em; margin: 0 0 12px; }
  .meta a { color: #3b82f6; text-decoration: none; }
  .stats-bar { display: flex; gap: 8px; margin-bottom: 12px; }
  .stat { background: white; border-radius: 10px; padding: 10px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
  .stat .num { font-size: 1.3em; font-weight: 700; display: block; line-height: 1.2; }
  .stat .lbl { font-size: 0.75em; color: #888; text-transform: uppercase; letter-spacing: 0.04em; }

  .toolbar { display: flex; gap: 6px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
  .toolbar input { flex: 1; min-width: 160px; padding: 6px 10px; border: 1px solid #d4d4d7; border-radius: 8px; font-size: 12px; background: white; }
  .btn { display: inline-block; padding: 5px 12px; border: none; border-radius: 6px; font-size: 11px; font-weight: 500;
         cursor: pointer; background: #3b82f6; color: white; text-decoration: none; white-space: nowrap; }
  .btn-sm { padding: 3px 8px; font-size: 11px; }
  .btn-outline { background: transparent; border: 1px solid #d4d4d7; color: #555; }
  .btn-outline:hover { background: #f0f0f2; }
  .btn-outline.active { background: #3b82f6; color: white; border-color: #3b82f6; }

  .cat-filters { margin-bottom: 10px; }
  .cat-group { display: inline-flex; align-items: center; gap: 4px; margin: 2px 12px 2px 0; }
  .cat-group-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #888; white-space: nowrap; }
  .cat-btn { font-size: 11px; padding: 2px 8px; border: 1px solid #d4d4d7; border-radius: 6px; background: white; cursor: pointer; color: #555; }
  .cat-btn.active { background: #3b82f6; color: white; border-color: #3b82f6; }
  .cat-btn-clear { font-size: 10px; padding: 2px 6px; color: #888; }

  .table-wrap { overflow-x: auto; background: white; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); position: relative; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; }
  thead { position: sticky; top: 0; z-index: 2; }
  th { background: #fafafa; padding: 8px 10px; font-size: 10px; font-weight: 600; text-transform: uppercase;
       letter-spacing: 0.04em; color: #888; text-align: left; cursor: pointer; user-select: none;
       border-bottom: 1px solid #e8e8ed; position: relative; overflow: hidden; white-space: nowrap; }
  th:hover { color: #1d1d1f; }
  th.sort-asc, th.sort-desc { color: #1d1d1f; }
  th.num, td.num { text-align: right; }
  .resize-grip { position: absolute; right: 0; top: 0; bottom: 0; width: 4px; cursor: col-resize; z-index: 3; }
  .resize-grip:hover { background: #3b82f6; }

  td { padding: 8px 10px; border-bottom: 1px solid #f0f0f2; cursor: pointer; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  table.wrap td { white-space: normal; word-break: break-word; }
  tr:hover td { background: #f8f8fa; }

  .col-date { width: 65px; }
  .col-title { width: 220px; }
  .col-creator { width: 120px; }
  .col-cat { width: 130px; }
  .col-price { width: 70px; }
  .col-online { width: 80px; }
  .col-desc { width: auto; }
  .col-score { width: 80px; }
  .col-actions { width: 40px; }

  .col-date { font-size: 11px; color: #888; }
  .col-title a { color: #1d1d1f; text-decoration: none; font-weight: 500; }
  .col-title a:hover { color: #3b82f6; }
  .col-creator { font-size: 12px; }
  .col-price { font-family: 'SF Mono', 'Menlo', monospace; font-size: 12px; }
  .col-online { font-family: 'SF Mono', 'Menlo', monospace; font-size: 12px; }
  .col-online a { color: #059669; text-decoration: none; font-weight: 500; }
  .col-online a:hover { text-decoration: underline; }
  .col-desc ul.bullets { margin: 0; padding-left: 14px; font-size: 11px; color: #555; line-height: 1.4; }
  .col-desc ul.bullets li { margin: 0; }
  .col-desc .desc-text { font-size: 11px; color: #555; }

  .tag { display: inline-block; font-size: 10px; padding: 1px 7px; border-radius: 5px; font-weight: 500; letter-spacing: 0.02em; }
  .tag-high { background: #d1fae5; color: #065f46; }
  .tag-medium { background: #fef3c7; color: #92400e; }
  .tag-low { background: #e5e7eb; color: #374151; }
  .tag-unscored { background: #e5e7eb; color: #888; }
  .tag-download { background: #3b82f6; color: white; }
  .tag-consider { background: #f59e0b; color: white; }
  .tag-skip { background: #9ca3af; color: white; }
  .tag-project { background: #ede9fe; color: #5b21b6; }

  .score-bar { display: inline-block; width: 40px; height: 5px; background: #e8e8ed; border-radius: 3px; vertical-align: middle; margin-right: 3px; }
  .score-bar span { display: block; height: 100%; border-radius: 3px; background: #3b82f6; }

  .empty-msg { text-align: center; color: #888; padding: 30px; font-size: 13px; }

  .detail-panel { background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-top: 12px; padding: 20px; }
  .detail-panel.hidden { display: none; }
  .detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
  .detail-header h3 { margin: 0; font-size: 1.15em; }
  .detail-header h3 a { color: #1d1d1f; text-decoration: none; }
  .detail-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
  .detail-grid div { font-size: 12px; line-height: 1.5; }
  .sub-meta { font-size: 10px; color: #888; display: block; }
  .detail-section { margin: 10px 0; }
  .detail-section strong { font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: #888; display: block; margin-bottom: 4px; }
  .detail-section p { font-size: 13px; margin: 4px 0; line-height: 1.5; }
  .detail-section pre { font-size: 11px; background: #f5f5f7; padding: 10px; border-radius: 8px; white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
  .detail-section ul.bullets { margin: 4px 0; padding-left: 20px; }
  .detail-section ul.bullets li { font-size: 13px; margin: 3px 0; line-height: 1.45; }
  .detail-actions { display: flex; gap: 8px; margin-top: 14px; }

  .scan-log { margin-top: 20px; font-size: 12px; color: #888; }
  .scan-log h4 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 6px; }
  .scan-log ul { margin: 0; padding: 0; list-style: none; }
  .scan-log li { padding: 2px 0; }

  @media (max-width: 900px) {
    .detail-grid { grid-template-columns: 1fr 1fr; }
    .col-desc { display: none; }
    .col-online { display: none; }
  }
</style>
"""
