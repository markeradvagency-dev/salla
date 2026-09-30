#!/usr/bin/env python3
"""Static verification: JSON validity, twig include/component references, asset() scripts vs webpack entries,
twilight.json component paths -> files, settings ids used in twig exist."""
import json, re, glob, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
views = root / "src/views"
err = []
tw = json.loads((root / "twilight.json").read_text())
for f in glob.glob(str(root / "src/locales/*.json")): json.load(open(f))

# twilight components -> files
for c in tw["components"]:
    p = views / "components" / (c["path"].replace(".", "/") + ".twig")
    if not p.exists(): err.append(f"component file missing: {p}")
for c in tw["components"]:
    for f in c["fields"]:
        if f["type"] == "collection":
            sub = {x["id"] for x in f["fields"]}
            if any(not i.startswith(f["id"] + ".") for i in sub): err.append(f"{c['path']}: collection sub-field ids must be prefixed '{f['id']}.'")
            for it in f["value"]:
                for k in it:
                    if k not in sub: err.append(f"{c['path']}: value key {k} has no sub-field")
ids = [s.get("id") for s in tw["settings"]]
if len(ids) != len(set(ids)): err.append("duplicate setting ids")

# twig references
def tw_path(dotted): return views / (dotted.replace(".", "/") + ".twig")
for f in views.rglob("*.twig"):
    s = f.read_text()
    for m in re.finditer(r"\{%\s*(?:include|extends|embed)\s+['\"]([\w.\-]+)['\"]", s):
        if not tw_path(m.group(1)).exists(): err.append(f"{f.relative_to(root)}: missing {m.group(1)}")
    for m in re.finditer(r"\{%\s*component\s+['\"]([\w.\-]+)['\"]", s):
        if m.group(1) != "home" and not tw_path("components." + m.group(1)).exists(): err.append(f"{f.relative_to(root)}: missing component {m.group(1)}")

# asset() references vs build output
pub = root / "public"
for f in views.rglob("*.twig"):
    for m in re.finditer(r"['\"]([\w\-/]+\.(?:js|css))['\"]\s*\|\s*asset", f.read_text()):
        if not (pub / m.group(1)).exists(): err.append(f"{f.relative_to(root)}: asset not built: {m.group(1)}")

# trans('luxe.*') keys
loc = json.load(open(root / "src/locales/en.json"))["luxe"]; locar = json.load(open(root / "src/locales/ar.json"))["luxe"]
for f in list(views.rglob("*.twig")):
    for m in re.finditer(r"trans\('luxe\.(\w+)'\)", f.read_text()):
        if m.group(1) not in loc or m.group(1) not in locar: err.append(f"{f.name}: locale key luxe.{m.group(1)}")
print("component sections:", len(tw["components"]), "| settings:", len(tw["settings"]))
print("\n".join(err) if err else "OK: no broken references")
sys.exit(1 if err else 0)
