#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round 4: revolve axis labels (world + user)."""
import sys
sys.path.insert(0, "tools")
from patch_gaps4_data import RU4

F = "src/app/Application_Dialogs.cpp"
src = open(F, encoding="utf-8").read()
pairs = [
    ("current = worldLabels[std::clamp(m_revolveWorldAxisIdx, 0, 2)];",
     "current = materializr::tr(\n"
     "            worldLabels[std::clamp(m_revolveWorldAxisIdx, 0, 2)]);"),
    ("if (ImGui::Selectable(userLabels[i], sel)) {",
     "if (ImGui::Selectable(materializr::tr(userLabels[i]), sel)) {"),
]
for old, new in pairs:
    if new in src: continue
    if old not in src:
        print("!! NOT FOUND:", old[:60]); sys.exit(1)
    src = src.replace(old, new, 1)
open(F, "w", encoding="utf-8").write(src)
print("patched", F)

PYFILE = "tools/i18n_catalogue.py"
py = open(PYFILE, encoding="utf-8").read()
if "RU_GAPS4" in py:
    print("catalogue: round-4 keys already registered")
else:
    def pylit(s):
        s = (s.replace("\\", "\\\\").replace('"', '\\"')
              .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
        return '"' + s + '"'
    block = ["\n# ---- Gap-fill round 4 (axis labels) ----\n", "RU_GAPS4 = {\n"]
    for en, ru in sorted(RU4.items()):
        block.append("    %s: %s,\n" % (pylit(en), pylit(ru)))
    block.append("}\n\nfor _en, _ru in RU_GAPS4.items():\n"
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
    print("catalogue: %d round-4 keys registered" % len(RU4))
print("now run: python3 tools/i18n_catalogue.py")
