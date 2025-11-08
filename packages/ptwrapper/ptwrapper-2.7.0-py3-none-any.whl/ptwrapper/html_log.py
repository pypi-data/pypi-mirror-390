# *************************************************************************** #
# This file is subject to the terms and conditions defined in the             #
# file 'LICENSE.txt', which is part of this source code package.              #
#                                                                             #
# No part of the package, including this file, may be copied, modified,       #
# propagated, or distributed except according to the terms contained in       #
# the file 'LICENSE.txt'.                                                     #
#                                                                             #
# (C) Copyright European Space Agency, 2025                                   #
# *************************************************************************** #
import re
import json
from collections import defaultdict, OrderedDict
from bs4 import BeautifulSoup
from datetime import datetime

def generate_html_header():
    return '''<!DOCTYPE html>
<html>
<head>
<title>PTR Debugging Log</title>
'''


def generate_body_and_headings_style():
    return '''
<style>
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f0f0f5;
        color: #444;
        margin: 10;
        padding: 10;
    }
    h1 {
        text-align: left;
        color: #2c3e50;
        font-size: 24px;
        margin-top: 20px;
    }
    h2, h3, h4 {
        color: #34495e;
        font-size: 18px;
        margin-top: 20px;
    }
</style>
'''


def generate_table_style():
    return '''
<style>
    table {
        width: 90%;
        margin: 20px 0 20px 20px;
        border-collapse: collapse;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        background-color: white;
        border-radius: 5px;
        overflow: hidden;
    }
    th {
        background-color: #2980b9;
        color: #fff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-align: left;
    }
    td {
        border-bottom: 1px solid #ddd;
        text-align: left;
    }
    tr:last-child td {
        border-bottom: none;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .error {
        color: #e74c3c;
    }
    .warning {
        color: #f39c12;
    }
    .info {
        color: #3498db;
    }
    table th, table td {
        border: none;
    }
    .table-header {
        background-color: #2980b9;
        color: white;
    }
    td:first-child {
        width: 175px;
        text-align: left !important;
    }
    td:nth-child(2) {
        width: 35px;
        text-align: left !important;
    }
    td:nth-child(3) {
        width: 100px;
        text-align: left !important;
    }
    td:nth-child(4) {
        width: auto;
        text-align: left !important;
    }
</style>
'''


def generate_html_body_start():
    return '''
</head>
<body>
    <h1>PTR Debugging Log</h1>
        <p style="color: #555;">
        This log contains a section to detect early problems with slews in the timeline (SLEW ESTIMATOR), 
        a section per Pointing designer that provides the messages for their specific blocks, and a
        section with a time-ordered timeline including all the blocks (TIMELINE). 
    </p>       
'''

def generate_html_header_and_style():
    return (
        generate_html_header()
        + generate_body_and_headings_style()
        + generate_table_style()
        + generate_html_body_start()
    )


def generate_block_section(block_key, block_value):
    # Skip empty block header
    html_line = f'<h3>{block_key} - {block_value["observation"]} [{block_value["start_time"]} - {block_value["end_time"]}]'

    # See if the block has a status
    if "status" in block_value and block_value["status"] != None:
        html_line += f' - {block_value["status"]}</h3>'
    else:
        html_line += f'</h3>'

    if html_line == '<h3> -  [ - ] </h3>':
        return ''

    html = html_line + '\n<table>'
    for error in block_value["error_messages"]:
        severity_class = error['severity'].lower()
        if error['text'][0] == '':
            error['text'] = error['text'][1:]
        html += f'''
        <tr class="{severity_class}">
            <td>{error["time"]}</td>
            <td>{error["percentage"]}</td>
            <td>{error["severity"]}</td>
            <td>{error["text"]}</td>
        </tr>
        '''
    html += '</table><br>'
    return html


def generate_designer_section(designer_key, designer_value):
    html = f'<h2>{designer_key}</h2>'
    for block_key, block_value in designer_value.items():
        html += generate_block_section(block_key, block_value)

    return html


def parse_time(t):
    # Convert '2032-12-19T23:54:02Z' into datetime for sorting
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")


def create_html_log(data_dict):
    html_content = generate_html_header_and_style()

    for designer_key, designer_value in data_dict.items():
        html_content += generate_designer_section(designer_key, designer_value)

    html_content += '''
    </body>
    </html>
    '''

    # Add index to HTML
    html_content = html_index(html_content)

    return html_content


def load_attitude_timeline(log_file):
    with open(log_file, 'r') as file:
        osve_log = json.load(file)

    timeline = []
    capturing = False

    for entry in osve_log:
        module = entry.get("module")
        text = entry.get("text", "")
        if module in {"AGM", "AGE"} and "Initializing Attitude Timeline" in text:
            capturing = True
            timeline.append(entry)
            continue

        if capturing:
            if module != "AGM":
                capturing = False
            else:
                timeline.append(entry)

    return timeline


def extract_slew_blocks(timeline):
    slew_log = []
    slew = {}
    recording = False

    for entry in timeline:
        text = entry.get("text", "")
        time = entry.get("time")

        if "Invalid slew due to attitude constraint breaks found" in text:
            if slew:
                slew_log.append(slew)
            slew = {
                "error_messages": ["Problems occur computing SLEW"],
                "block_name": [],
                "block_instrument": []
            }
            recording = True

        if recording:
            if "Problems occur computing slew" in text or "During slew checking" in text:
                slew["time"] = time
            elif "would solve breaks" in text:
                msg = text.split("TimelineHandler: ")[-1]
                slew["error_messages"].append(msg)

    if slew:
        slew_log.append(slew)

    return slew_log


def associate_slew_blocks(slew_log, ptr_log):
    for slew in slew_log:
        for instrument, blocks in ptr_log.items():
            for block_name, block_log in blocks.items():
                if slew.get("time") == block_log.get("start_time") and " SLEW " in block_name:
                    slew["block_name"].append(block_name)
                    slew["block_instrument"].append(instrument)


def format_slew_entry(slew):
    error_messages = []
    for msg in slew["error_messages"]:
        severity = "INFO" if "would solve breaks" in msg else "ERROR"
        error_messages.append({
            "percentage": "-",
            "severity": severity,
            "time": slew["time"],
            "text": msg
        })

    try:
        block_name = " ".join(
            f"{name} ({instr})"
            for name, instr in zip(slew["block_name"], slew["block_instrument"])
        )
    except Exception:
        block_name = " ".join(slew["block_name"])

    return block_name, {
        "observation": "",
        "start_time": slew["time"],
        "end_time": slew["time"],
        "error_messages": error_messages
    }


def merge_logs(ptr_log, osve_log_file):
    timeline = load_attitude_timeline(osve_log_file)
    slew_log = extract_slew_blocks(timeline)
    associate_slew_blocks(slew_log, ptr_log)

    if not slew_log:
        return ptr_log

    ptr_log["SLEW ESTIMATOR"] = {
        format_slew_entry(slew)[0]: format_slew_entry(slew)[1]
        for slew in slew_log
    }

    return ptr_log


def extract_agm_entries(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    capturing = False
    extracted = []

    for entry in data:
        # Check if we're about to start capturing:
        if entry.get("module") == "AGM" and "Initializing Attitude Timeline" in entry.get("text", ""):
            # We found the line indicating the start
            capturing = True
            extracted.append(entry)
            continue

        # If we're already capturing, keep going as long as we stay in module "AGM"
        if capturing:
            # If the module changed to something other than "AGM", we stop capturing
            if entry.get("module") != "AGM":
                capturing = False
            else:
                extracted.append(entry)

    return extracted


def parse_time(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


def build_global_timeline(data: dict, exclude_keys=("TIMELINE",), dedupe_on=("start_time", "end_time")) -> None:
    """
    Add a top-level 'TIMELINE' key containing all blocks from all instruments,
    sorted by start_time, skipping block names in exclude_keys,
    and removing duplicates based on dedupe_on fields.
    """
    all_blocks = []

    for instrument, blocks in data.items():
        if not isinstance(blocks, dict):
            continue
        for block_name, block_info in blocks.items():
            if block_name in exclude_keys:
                continue
            if not isinstance(block_info, dict):
                continue
            start = block_info.get("start_time")
            if not start:
                continue
            try:
                start_dt = parse_time(start)
            except ValueError:
                continue
            all_blocks.append((start_dt, instrument, block_name, block_info))

    # Sort all blocks by start_time
    all_blocks.sort(key=lambda x: x[0])

    # Build ordered dict without duplicates
    seen = set()
    timeline_dict = OrderedDict()
    for _, instr, blk_name, blk_info in all_blocks:
        dedupe_key = tuple(blk_info.get(f) for f in dedupe_on)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        merged_name = f"{instr} - {blk_name}"
        timeline_dict[merged_name] = blk_info

    # Add to top-level
    data["TIMELINE"] = timeline_dict


def reorder_dict(d, first_key):
    """
    Returns a new dictionary that puts `first_key` first (if present),
    followed by the other keys in alphabetical order.
    """
    new_dict = {}

    # 1. If the special key is in `d`, add it first
    if first_key in d:
        new_dict[first_key] = d[first_key]

    # 2. Add the remaining keys in alphabetical order
    for key in sorted(d.keys()):
        if key != first_key:
            new_dict[key] = d[key]

    # 3. Create a copy of the without the SLEW ESTIMATOR that provides a timer ordered timeline
    build_global_timeline(new_dict, exclude_keys=('TIMELINE'))

    return new_dict


def slugify(text):
    text = re.sub(r"\s+", "-", text.strip().lower())
    text = re.sub(r"[^a-z0-9\-]", "", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "section"


def html_index(html_body):
    try:
        soup = BeautifulSoup(html_body, "lxml")
    except Exception:
        soup = BeautifulSoup(html_body, "html.parser")

    # Track used IDs
    used_ids = set(tag.get("id") for tag in soup.find_all(attrs={"id": True}))

    def ensure_id(tag, prefix=None, counter=defaultdict(int)):
        if tag.get("id"):
            used_ids.add(tag["id"])
            return tag["id"]
        base = slugify(tag.get_text(" ", strip=True))
        if prefix:
            base = f"{prefix}-{base}"
        new_id = base or "section"
        while new_id in used_ids:
            counter[base] += 1
            new_id = f"{base}-{counter[base]}"
        tag["id"] = new_id
        used_ids.add(new_id)
        return new_id

    # Build nested TOC by streaming headings in document order
    headings = soup.find_all(["h2", "h3"])

    toc_div = soup.new_tag("div", id="index")
    toc_title = soup.new_tag("h2")
    toc_title.string = "Index"
    toc_div.append(toc_title)
    root_ul = soup.new_tag("ul")

    current_h2_li = None
    for tag in headings:
        if tag.name == "h2":
            h2_id = ensure_id(tag, prefix="h2")
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=f"#{h2_id}")
            a.string = tag.get_text(strip=True)
            li.append(a)
            root_ul.append(li)
            current_h2_li = li
        elif tag.name == "h3":
            # attach under the most recent h2
            if current_h2_li is None:
                # No preceding h2; skip or attach at root
                current_h2_li = soup.new_tag("li")
                current_h2_li.string = "(Orphan subsections)"
                root_ul.append(current_h2_li)
            sub_ul = current_h2_li.find("ul")
            if not sub_ul:
                sub_ul = soup.new_tag("ul")
                current_h2_li.append(sub_ul)
            h3_id = ensure_id(tag, prefix="h3")
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=f"#{h3_id}")
            a.string = tag.get_text(strip=True)
            li.append(a)
            sub_ul.append(li)

    toc_div.append(root_ul)

    # Insert TOC after first <p> if present, else at top of <body>
    p = soup.find("p")
    if p:
        p.insert_after(toc_div)
    else:
        (soup.body or soup).insert(0, toc_div)

    # ---- Append "[index]" link INSIDE each h2/h3 title ----
    def append_index_link_inside(heading):
        # remove any existing back link to avoid duplicates
        for a in heading.find_all("a", class_="back-to-index"):
            a.decompose()
        # trailing space
        heading.append(" ")
        link = soup.new_tag("a", href="#index", **{"class": "back-to-index"})
        link.string = "[index]"
        heading.append(link)

    for tag in headings:
        ensure_id(tag, prefix=tag.name)  # ensure ids exist
        append_index_link_inside(tag)

    # Styling
    style_tag = soup.new_tag("style")
    style_tag.string = """
    #index { background:#fff; border:1px solid #e5e7eb; border-radius:6px; padding:12px 16px; margin:16px 0; }
    #index ul { list-style: none; padding-left: 0; margin: 0; }
    #index > ul > li { margin: 6px 0; }
    #index ul ul { padding-left: 18px; }
    #index a { text-decoration: none; }
    #index a:hover { text-decoration: underline; }
    .back-to-index {
        font-size: 0.85em;
        margin-left: 8px;
        text-decoration: none;
        color: #2980b9;
    }
    .back-to-index:hover {
        text-decoration: underline;
    }
    """
    (soup.head or soup).append(style_tag)

    return str(soup)