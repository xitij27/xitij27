"""Keeps only the 3D calendar and the commits/issues/PRs radar in each image.

github-profile-3d-contrib always adds a language pie chart and a line of totals
(contributions, stars, forks, dates). The streak card already shows the totals,
so this removes both. The workflow runs it on every image after drawing.
Usage: python3 assets/trim_3d.py profile-3d-contrib/*.svg
"""
import sys
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)

for path in sys.argv[1:]:
    tree = ET.parse(path)
    root = tree.getroot()
    groups = [el for el in root if el.tag == f"{{{SVG}}}g"]
    # The calendar is the big group of blocks; the radar is the group holding the .radar shape.
    calendar = max(groups, key=lambda g: sum(1 for _ in g.iter()))
    radar = next((g for g in groups if any(e.get("class") == "radar" for e in g.iter())), None)
    if radar is None or radar is calendar:
        sys.exit(f"{path}: couldn't find the radar chart; the tool's layout may have changed")
    for g in groups:
        if g is not calendar and g is not radar:
            root.remove(g)
    tree.write(path, encoding="unicode")
    print(f"{path}: kept the calendar and radar, removed {len(groups) - 2} other parts")
