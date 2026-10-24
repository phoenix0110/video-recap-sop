"""Parse progress.md + README.md and generate a self-contained HTML dashboard.

Usage:
    python generate_dashboard.py <project_dir>

Reads:  <project_dir>/progress/progress.md
        <project_dir>/README.md
Writes: <project_dir>/progress/dashboard.html
"""
import re
import sys
from datetime import datetime
from pathlib import Path

STEP_PATTERN = re.compile(r'^## (Step \d+[：:].+)$', re.M)
SUBSECTION_PATTERN = re.compile(r'^### (.+)$', re.M)
CHECKBOX_CHECKED = re.compile(r'^- \[x\] (.+)$', re.M | re.I)
CHECKBOX_UNCHECKED = re.compile(r'^- \[ \] (.+)$', re.M)
META_PATTERN = re.compile(r'^\*\*(.+?)[:：]\*\*\s*`?(.+?)`?\s*$', re.M)


def parse_readme(project_dir: Path) -> dict:
    readme = project_dir / "README.md"
    if not readme.exists():
        return {"project_name": project_dir.name, "sources": []}
    text = readme.read_text(encoding="utf-8")
    title_match = re.search(r'^# (.+)$', text, re.M)
    name = title_match.group(1).strip() if title_match else project_dir.name
    rows = re.findall(r'\|\s*\d+\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|', text)
    sources = []
    for row in rows:
        parts = [c.strip() for c in row]
        sources.append({"role": parts[0], "title": parts[1], "channel": parts[2], "duration": parts[3]})
    return {"project_name": name, "sources": sources}


def parse_progress(project_dir: Path) -> list:
    progress_file = project_dir / "progress" / "progress.md"
    if not progress_file.exists():
        raise FileNotFoundError(f"Progress file not found: {progress_file}")
    text = progress_file.read_text(encoding="utf-8")

    meta = {}
    header_block = text.split("---")[1] if text.count("---") >= 2 else ""
    for m in META_PATTERN.finditer(header_block):
        meta[m.group(1).strip()] = m.group(2).strip()

    step_splits = STEP_PATTERN.split(text)
    steps = []
    for i in range(1, len(step_splits), 2):
        step_title = step_splits[i].strip()
        step_body = step_splits[i + 1] if i + 1 < len(step_splits) else ""
        sub_splits = SUBSECTION_PATTERN.split(step_body)
        subsections = []
        main_body = sub_splits[0]
        checked = CHECKBOX_CHECKED.findall(main_body)
        unchecked = CHECKBOX_UNCHECKED.findall(main_body)
        if checked or unchecked:
            items = []
            for line in main_body.splitlines():
                cm = re.match(r'^- \[([ xX])\] (.+)$', line)
                if cm:
                    items.append({"text": cm.group(2), "done": cm.group(1).lower() == 'x'})
            if items:
                subsections.append({"title": None, "items": items})

        for j in range(1, len(sub_splits), 2):
            sub_title = sub_splits[j].strip()
            sub_body = sub_splits[j + 1] if j + 1 < len(sub_splits) else ""
            items = []
            for line in sub_body.splitlines():
                cm = re.match(r'^- \[([ xX])\] (.+)$', line)
                if cm:
                    items.append({"text": cm.group(2), "done": cm.group(1).lower() == 'x'})
            if items:
                subsections.append({"title": sub_title, "items": items})

        total = sum(len(s["items"]) for s in subsections)
        done = sum(sum(1 for it in s["items"] if it["done"]) for s in subsections)
        steps.append({
            "title": step_title,
            "subsections": subsections,
            "total": total,
            "done": done,
        })
    return meta, steps


def step_status(step: dict) -> str:
    if step["done"] == step["total"] and step["total"] > 0:
        return "completed"
    elif step["done"] > 0:
        return "in_progress"
    return "pending"


def generate_html(meta: dict, steps: list, readme_info: dict) -> str:
    total_items = sum(s["total"] for s in steps)
    total_done = sum(s["done"] for s in steps)
    pct = round(total_done / total_items * 100) if total_items else 0

    current_step = None
    for i, s in enumerate(steps):
        if step_status(s) == "in_progress":
            current_step = i + 1
            break
    if current_step is None:
        for i, s in enumerate(steps):
            if step_status(s) == "pending":
                current_step = i + 1
                break

    project_name = readme_info.get("project_name", meta.get("项目名称", "Unknown Project"))
    sources_html = ""
    for src in readme_info.get("sources", []):
        sources_html += f'<div class="source-item"><span class="source-role">{src["role"]}</span>{src["title"]} — {src["channel"]} ({src["duration"]})</div>'
    if not sources_html:
        sources_html = '<div class="source-item">No source info in README.md</div>'

    steps_html = ""
    for i, s in enumerate(steps):
        status = step_status(s)
        status_icon = {"completed": "&#10003;", "in_progress": "&#9654;", "pending": "&#9679;"}[status]
        step_pct = round(s["done"] / s["total"] * 100) if s["total"] else 0

        items_html = ""
        for sub in s["subsections"]:
            if sub["title"]:
                items_html += f'<div class="sub-title">{sub["title"]}</div>'
            for it in sub["items"]:
                check_cls = "item-done" if it["done"] else "item-pending"
                check_icon = "&#10003;" if it["done"] else "&#9744;"
                items_html += f'<div class="check-item {check_cls}"><span class="check-icon">{check_icon}</span>{it["text"]}</div>'

        is_current = "step-current" if status == "in_progress" else ""
        steps_html += f'''
        <div class="step-card {status} {is_current}" onclick="this.classList.toggle('expanded')">
            <div class="step-header">
                <div class="step-icon">{status_icon}</div>
                <div class="step-info">
                    <div class="step-title">{s["title"]}</div>
                    <div class="step-progress-bar"><div class="step-progress-fill" style="width:{step_pct}%"></div></div>
                </div>
                <div class="step-count">{s["done"]}/{s["total"]}</div>
            </div>
            <div class="step-details">{items_html}</div>
        </div>'''

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_label = f"Step {current_step}" if current_step else "All Done"

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{project_name} — Progress Dashboard</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, "Segoe UI", Roboto, "Noto Sans SC", sans-serif; background: #0f1117; color: #e0e0e0; min-height: 100vh; padding: 24px; }}
.container {{ max-width: 800px; margin: 0 auto; }}
.header {{ background: linear-gradient(135deg, #1a1d2e 0%, #252940 100%); border-radius: 16px; padding: 32px; margin-bottom: 24px; border: 1px solid #2a2e42; }}
.project-name {{ font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 8px; }}
.header-meta {{ font-size: 13px; color: #8b8fa3; margin-bottom: 16px; }}
.sources {{ margin-bottom: 20px; }}
.source-item {{ font-size: 13px; color: #9ca0b4; padding: 4px 0; }}
.source-role {{ display: inline-block; background: #2a2e42; color: #7c8aff; border-radius: 4px; padding: 1px 8px; margin-right: 8px; font-size: 12px; }}
.overall {{ margin-top: 16px; }}
.overall-bar {{ height: 8px; background: #1e2133; border-radius: 4px; overflow: hidden; margin-top: 8px; }}
.overall-fill {{ height: 100%; background: linear-gradient(90deg, #4f5bff 0%, #7c8aff 100%); border-radius: 4px; transition: width 0.5s ease; }}
.overall-stats {{ display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }}
.overall-pct {{ font-size: 28px; font-weight: 700; color: #7c8aff; }}
.overall-detail {{ font-size: 13px; color: #8b8fa3; text-align: right; }}
.step-card {{ background: #1a1d2e; border-radius: 12px; margin-bottom: 8px; border: 1px solid #2a2e42; overflow: hidden; cursor: pointer; transition: border-color 0.2s; }}
.step-card:hover {{ border-color: #3d4260; }}
.step-card.step-current {{ border-color: #4f5bff; box-shadow: 0 0 0 1px #4f5bff33; }}
.step-header {{ display: flex; align-items: center; padding: 16px 20px; gap: 16px; }}
.step-icon {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }}
.completed .step-icon {{ background: #1a3a2a; color: #4caf50; }}
.in_progress .step-icon {{ background: #2a2640; color: #7c8aff; }}
.pending .step-icon {{ background: #1e2133; color: #555; }}
.step-info {{ flex: 1; min-width: 0; }}
.step-title {{ font-size: 14px; font-weight: 600; color: #e0e0e0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.step-progress-bar {{ height: 4px; background: #1e2133; border-radius: 2px; margin-top: 6px; overflow: hidden; }}
.step-progress-fill {{ height: 100%; border-radius: 2px; transition: width 0.5s ease; }}
.completed .step-progress-fill {{ background: #4caf50; }}
.in_progress .step-progress-fill {{ background: #7c8aff; }}
.pending .step-progress-fill {{ background: #333; }}
.step-count {{ font-size: 13px; color: #8b8fa3; flex-shrink: 0; white-space: nowrap; }}
.step-details {{ display: none; padding: 0 20px 16px 68px; }}
.step-card.expanded .step-details {{ display: block; }}
.sub-title {{ font-size: 13px; font-weight: 600; color: #9ca0b4; margin: 12px 0 6px 0; padding-bottom: 4px; border-bottom: 1px solid #252940; }}
.check-item {{ font-size: 13px; padding: 4px 0; display: flex; align-items: flex-start; gap: 8px; line-height: 1.5; }}
.check-icon {{ flex-shrink: 0; width: 18px; text-align: center; }}
.item-done {{ color: #6b7a6d; }}
.item-done .check-icon {{ color: #4caf50; }}
.item-pending {{ color: #c0c4d8; }}
.item-pending .check-icon {{ color: #555; }}
.footer {{ text-align: center; font-size: 12px; color: #555; margin-top: 24px; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="project-name">{project_name}</div>
        <div class="header-meta">Generated {now} &nbsp;|&nbsp; Current: {current_label}</div>
        <div class="sources">{sources_html}</div>
        <div class="overall">
            <div class="overall-stats">
                <div class="overall-pct">{pct}%</div>
                <div class="overall-detail">{total_done} / {total_items} items<br>7 steps</div>
            </div>
            <div class="overall-bar"><div class="overall-fill" style="width:{pct}%"></div></div>
        </div>
    </div>
    {steps_html}
    <div class="footer">Video Recap SOP Progress Dashboard</div>
</div>
</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_dashboard.py <project_dir>")
        sys.exit(1)
    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.is_dir():
        print(f"Error: Not a directory: {project_dir}")
        sys.exit(1)

    readme_info = parse_readme(project_dir)
    meta, steps = parse_progress(project_dir)

    html = generate_html(meta, steps, readme_info)
    out = project_dir / "progress" / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    total = sum(s["total"] for s in steps)
    done = sum(s["done"] for s in steps)
    print(f"Dashboard generated: {out}")
    print(f"Progress: {done}/{total} ({round(done/total*100) if total else 0}%)")
    for s in steps:
        icon = {"completed": "[DONE]", "in_progress": "[>>>]", "pending": "[   ]"}[step_status(s)]
        print(f"  {icon} {s['title']} ({s['done']}/{s['total']})")


if __name__ == "__main__":
    main()
