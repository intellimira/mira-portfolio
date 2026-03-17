#!/usr/bin/env python3
"""
MIRA Portfolio Generator
Scans /projects/ and generates portfolio HTML based on publish flags.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

PROJECTS_DIR = Path("/home/sir-v/MiRA/projects")
OUTPUT_DIR = Path("/home/sir-v/MiRA/projects/mira-portfolio/output")

SECTIONS = {
    "business": {
        "title": "Business",
        "description": "Client projects, Shadow Ops, and revenue-generating solutions",
        "icon": "💼",
    },
    "agents": {
        "title": "Agents",
        "description": "Technical AI agent work, MIRA system, and skills",
        "icon": "🤖",
    },
    "whatif": {
        "title": "What-If",
        "description": "Emerging ideas and experimental projects",
        "icon": "💡",
    },
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | MIRA Portfolio</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a12 0%, #1a1a2e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        header {{ text-align: center; margin-bottom: 60px; }}
        h1 {{ font-size: 3rem; margin-bottom: 10px; background: linear-gradient(90deg, #64b5a0, #c9a227); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .subtitle {{ color: #888; font-size: 1.2rem; }}
        
        .section {{ margin-bottom: 60px; }}
        .section-header {{ 
            display: flex; align-items: center; gap: 15px; 
            margin-bottom: 30px; padding-bottom: 15px;
            border-bottom: 2px solid #64b5a0;
        }}
        .section-icon {{ font-size: 2.5rem; }}
        .section-title {{ font-size: 2rem; color: #64b5a0; }}
        .section-desc {{ color: #888; margin-left: auto; }}
        
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }}
        
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border-color: #64b5a0;
        }}
        
        .card-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4rem;
        }}
        
        .card-content {{ padding: 20px; }}
        .card-title {{ font-size: 1.3rem; margin-bottom: 10px; color: #fff; }}
        .card-desc {{ color: #aaa; font-size: 0.9rem; line-height: 1.5; margin-bottom: 15px; }}
        
        .card-meta {{
            display: flex; gap: 10px; flex-wrap: wrap;
        }}
        .tag {{
            background: rgba(100, 181, 160, 0.2);
            color: #64b5a0;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px;
            color: #666;
        }}
        
        footer {{ text-align: center; padding: 40px; color: #666; border-top: 1px solid #333; margin-top: 60px; }}
        .nav {{ display: flex; justify-content: center; gap: 30px; margin-bottom: 20px; }}
        .nav a {{ color: #64b5a0; text-decoration: none; }}
        .nav a:hover {{ text-decoration: underline; }}
        
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            h1 {{ font-size: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 MIRA Portfolio</h1>
            <p class="subtitle">AI Agent Systems • Business Solutions • Innovation Lab</p>
            <p style="margin-top: 20px; color: #666;">{update_date}</p>
        </header>
        
        {sections}
        
        <footer>
            <div class="nav">
                <a href="#business">Business</a>
                <a href="#agents">Agents</a>
                <a href="#whatif">What-If</a>
            </div>
            <p>Built with MIRA • {year}</p>
        </footer>
    </div>
</body>
</html>
"""

SECTION_TEMPLATE = """
<section class="section" id="{id}">
    <div class="section-header">
        <span class="section-icon">{icon}</span>
        <h2 class="section-title">{title}</h2>
        <span class="section-desc">{description}</span>
    </div>
    <div class="grid">
        {cards}
    </div>
</section>
"""

CARD_TEMPLATE = """
<div class="card">
    <div class="card-image">{emoji}</div>
    <div class="card-content">
        <h3 class="card-title">{title}</h3>
        <p class="card-desc">{description}</p>
        <div class="card-meta">
            {tags}
        </div>
    </div>
</div>
"""


def get_publish_flags():
    """Load publish configuration."""
    config_path = PROJECTS_DIR / "publish_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def detect_section(project_name, content):
    """Auto-detect section based on project name or content."""
    name_lower = project_name.lower()
    content_lower = content.lower()

    if any(
        x in name_lower
        for x in [
            "shadow",
            "client",
            "cfo",
            "payroll",
            "kyc",
            "fintech",
            "logistics",
            "compliance",
            "margin",
            "inventory",
            "kitchen",
            "clinic",
            "property",
            "crm",
        ]
    ):
        return "business"
    if any(
        x in name_lower
        for x in ["skill", "agent", "mcp", "open", "notebook", "model", "ai-", "coding"]
    ):
        return "agents"
    if any(
        x in name_lower for x in ["what-if", "whatif", "experiment", "draft", "glean"]
    ):
        return "whatif"
    return None


def parse_project_index(index_path):
    """Parse project index.md to extract metadata."""
    with open(index_path) as f:
        content = f.read()

    title = index_path.parent.name.replace("-", " ").title()
    description = ""
    industry = ""

    lines = content.split("\n")
    in_overview = False
    for line in lines:
        if "## Project Overview" in line:
            in_overview = True
        elif in_overview and line.startswith("##"):
            in_overview = False
        elif in_overview:
            if "**Client**" in line:
                match = re.search(r"\*\*Client\*\*.*?\|\s*(.+?)\s*\|", line)
                if match:
                    title = match.group(1).strip()
            elif "**Industry**" in line:
                match = re.search(r"\*\*Industry\*\*.*?\|\s*(.+?)\s*\|", line)
                if match:
                    industry = match.group(1).strip()

    first_line = content.split("\n")[0]
    if "# " in first_line:
        title = first_line.replace("# ", "").strip()

    desc_match = re.search(r">(.+?)<", content)
    if desc_match:
        description = desc_match.group(1).strip()

    publish_match = re.search(r"publish:\s*(true|false)", content, re.IGNORECASE)
    is_published = publish_match.group(1).lower() == "true" if publish_match else False

    return {
        "title": title,
        "description": description or f"{industry} project"
        if industry
        else "MIRA project",
        "publish": is_published,
        "content": content,
    }


def find_project_images(project_dir):
    """Find images in project folder."""
    images = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.svg"]:
        images.extend(project_dir.glob(f"**/{ext}"))
    return images[:1]


def generate_portfolio():
    """Main generator function."""
    print("🔄 Scanning projects...")

    # Check if projects directory exists (required for generation)
    if not PROJECTS_DIR.exists():
        print(f"⚠️  Projects directory not found: {PROJECTS_DIR}")
        print("📦 Using existing index.html instead")
        return  # Exit gracefully, use existing HTML

    publish_flags = get_publish_flags()
    section_projects = {k: [] for k in SECTIONS}

    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        if project_dir.name.startswith(".") or project_dir.name == "mira-portfolio":
            continue

        index_path = project_dir / "docs" / "index.md"
        if not index_path.exists():
            continue

        try:
            project = parse_project_index(index_path)

            if not project["publish"]:
                if project_dir.name in publish_flags:
                    project["publish"] = publish_flags[project_dir.name]

            if not project["publish"]:
                print(f"  ⏭️  Skipping: {project_dir.name} (not published)")
                continue

            section = detect_section(project_dir.name, project["content"])
            if section is None:
                section = "whatif"

            images = find_project_images(project_dir)
            emoji = "📁"
            if (
                "health" in project["title"].lower()
                or "clinic" in project["title"].lower()
            ):
                emoji = "🏥"
            elif "kitchen" in project["title"].lower():
                emoji = "🍳"
            elif (
                "fintech" in project["title"].lower()
                or "cfo" in project["title"].lower()
            ):
                emoji = "💰"
            elif "skill" in project_dir.name.lower():
                emoji = "⚡"
            elif "agent" in project_dir.name.lower():
                emoji = "🤖"

            project_data = {
                "title": project["title"],
                "description": project["description"],
                "emoji": emoji,
                "tags": [section.capitalize()],
            }

            section_projects[section].append(project_data)
            print(f"  ✅ Added: {project['title']} -> {section}")

        except Exception as e:
            print(f"  ⚠️  Error processing {project_dir.name}: {e}")

    sections_html = ""
    for section_id, section_info in SECTIONS.items():
        projects = section_projects[section_id]

        if projects:
            cards_html = ""
            for p in projects:
                tags_html = "".join(f"<span class='tag'>{t}</span>" for t in p["tags"])
                cards_html += CARD_TEMPLATE.format(
                    emoji=p["emoji"],
                    title=p["title"],
                    description=p["description"],
                    tags=tags_html,
                )
        else:
            cards_html = "<div class='empty-state'>No published projects yet</div>"

        sections_html += SECTION_TEMPLATE.format(
            id=section_id,
            icon=section_info["icon"],
            title=section_info["title"],
            description=section_info["description"],
            cards=cards_html,
        )

    html = HTML_TEMPLATE.format(
        title="MIRA Portfolio",
        sections=sections_html,
        update_date=datetime.now().strftime("%B %d, %Y"),
        year=datetime.now().year,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "index.html"
    with open(output_path, "w") as f:
        f.write(html)

    print(f"\n🎉 Portfolio generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_portfolio()
