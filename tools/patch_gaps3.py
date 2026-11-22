#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round 3: auto-wrap window titles in Begin(), fix status bar selection."""
import sys
sys.path.insert(0, "tools")
from patch_gaps3_data import RU3

def patch(path, pairs):
    src = open(path, encoding="utf-8").read()
    dirty = False
    for old, new in pairs:
        if new in src: continue
        if old not in src:
            print("!! NOT FOUND in %s: %r" % (path, old[:70])); sys.exit(1)
        src = src.replace(old, new, 1); dirty = True
    if dirty:
        open(path, "w", encoding="utf-8").write(src)
    print("patched", path)

patch("src/ui/StatusBar.cpp", [
    ('std::snprintf(selText, sizeof(selText), "Selection: %s (%d)", typeName, count);',
     'std::snprintf(selText, sizeof(selText),\n'
     '                      materializr::tr("Selection: %s (%d)"),\n'
     '                      materializr::tr(typeName), count);'),
])

wrapped, missing = [], []

def wrap_file(path):
    src = open(path, encoding="utf-8").read()
    marker = 'ImGui::Begin("'
    out, i, found = [], 0, []
    while True:
        j = src.find(marker, i)
        if j < 0:
            out.append(src[i:]); break
        k = src.find('"', j + len(marker))
        if k < 0:
            out.append(src[i:]); break
        t = src[j + len(marker):k]
        if not t or t.startswith("##") or "###" in t or "\n" in t:
            out.append(src[i:k + 1]); i = k + 1; continue
        found.append(t)
        out.append(src[i:j] + 'ImGui::Begin(materializr::tr("' + t + '###' + t + '"),')
        i = k + 1
    new = "".join(out)
    if new != src:
        open(path, "w", encoding="utf-8").write(new)
    print("wrapped %d Begin titles in %s" % (len(found), path))
    wrapped.extend(found)

wrap_file("src/app/Application_Dialogs.cpp")
wrap_file("src/app/Application.cpp")
for t in wrapped:
    if t not in RU3:
        missing.append(t)
print("wrapping done: %d titles" % len(wrapped))

# ---- catalogue merge ----
PYFILE = "tools/i18n_catalogue.py"
py = open(PYFILE, encoding="utf-8").read()
if "RU_GAPS3" in py:
    print("catalogue: round-3 keys already registered")
else:
    def pylit(s):
        s = (s.replace("\\", "\\\\").replace('"', '\\"')
              .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
        return '"' + s + '"'
    entries = [("Selection: %s (%d)", RU3["Selection: %s (%d)"])]
    entries += [(t, RU3[t]) for t in sorted(RU3)
                if t != "Selection: %s (%d)" and t in wrapped]
    entries += [(t, "") for t in wrapped if t not in RU3]
    seen = set()
    block = ["\n# ---- Gap-fill round 3 (dialog titles, status bar) ----\n",
             "RU_GAPS3 = {\n"]
    for title, ru in entries:
        if title in seen: continue
        seen.add(title)
        key = title if "%" in title else title + "###" + title
        block.append("    %s: %s,\n" % (pylit(key), pylit(ru)))
    block.append("}\n\nfor _en, _ru in RU_GAPS3.items():\n"
                 "    for _entry in CAT:\n"
                 "        if _entry[0] == _en:\n"
                 "            if not _entry[1].get(\"ru\"):\n"
                 "                _entry[1][\"ru\"] = _ru\n"
                 "            break\n"
                 "    else:\n"
                 "        CAT.append((_en, {\"es\":\"\", \"pt\":\"\", \"fr\":\"\", "
                 "\"de\":\"\", \"it\":\"\", \"ru\":_ru}))\n")
    anchor = py.index("def cstr(")
    py = py[:anchor] + "".join(block) + "\n" + py[anchor:]
    open(PYFILE, "w", encoding="utf-8").write(py)
    print("catalogue: %d round-3 keys registered" % len(seen))

if missing:
    print("\n!! titles wrapped WITHOUT RU translation (next pass):")
    for t in missing:
        print("   -", repr(t))
else:
    print("all wrapped titles have RU translations")
print("now run: python3 tools/i18n_catalogue.py")
