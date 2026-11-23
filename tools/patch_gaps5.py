#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round 5: canvas buttons, sketch banner, inference labels, pattern titles,
welcome title, restore-all, layout menu, drawing-view labels."""
import sys, re
sys.path.insert(0, "tools")
from patch_gaps5_data import RU5

def edit(path, repls, regexps=()):
    src = open(path, encoding="utf-8").read()
    n = 0
    for old, new in repls:
        if new in src: continue
        if old not in src:
            print("!! NOT FOUND in %s: %r" % (path, old[:60])); sys.exit(1)
        src = src.replace(old, new, 1); n += 1
    for pat, rep in regexps:
        src, k = re.subn(pat, rep, src); n += k
    open(path, "w", encoding="utf-8").write(src)
    print("%s: %d правок" % (path, n))

VP = "src/app/Application_Viewport.cpp"
edit(VP, [
    ('bool clicked = wideButton(m_moveModeToggle ? "Move: On" : "Move: Off");',
     'const std::string moveLbl = materializr::trFormat(\n'
     '                    "Move: %s", materializr::tr(m_moveModeToggle ? "On" : "Off"));\n'
     '                bool clicked = wideButton(moveLbl.c_str());'),
    ('bool del = wideButton("Delete");',
     'bool del = wideButton(materializr::tr("Delete"));'),
    ('bool finish = wideButton("Finish");',
     'bool finish = wideButton(materializr::tr("Finish"));'),
    ('bool back = wideButton("Back");',
     'bool back = wideButton(materializr::tr("Back"));'),
    ('bool cancel = wideButton(chainTool ? "Cancel" : "Cancel Shape");',
     'bool cancel = wideButton(chainTool ? materializr::tr("Cancel")\n'
     '                                        : materializr::tr("Cancel Shape"));'),
    ('                ? "SKETCH MODE - Finish Sketch applies, Exit Sketch discards"\n'
     '                : "SKETCH MODE - Press Escape to finish");',
     '                ? materializr::tr("SKETCH MODE - Finish Sketch applies, Exit Sketch discards")\n'
     '                : materializr::tr("SKETCH MODE - Press Escape to finish"));'),
    ('ImGui::TextDisabled(drv ? "(controls geometry)"\n'
     '                                                        : "(measures only)");',
     'ImGui::TextDisabled("%s",\n'
     '                                    materializr::tr(drv ? "(controls geometry)"\n'
     '                                                    : "(measures only)"));'),
], regexps=[(
    r'(case InferenceGuide::(?:Endpoint|Midpoint|OnLine|OnCircle|AxisHFromPoint|'
    r'AxisVFromPoint|PerpToPrev|ParallelToPrev|OnLineExtension|TangentToCircle|'
    r'PerpToRef|Symmetry|CornerBisector|CornerTangent):\s*return )"([^"]+)";',
    r'\1materializr::tr("\2");')])

edit("src/app/Application.cpp", [
    ('ImGui::Button(nOrphans > 1 ? "Restore all" : "Restore it",',
     'ImGui::Button(nOrphans > 1 ? materializr::tr("Restore all")\n'
     '                                      : materializr::tr("Restore it"),')])

edit("src/app/Application_Dialogs.cpp", [
    ('? "Sketch Linear Pattern"\n'
     '                            : "Sketch Circular Pattern";',
     '? materializr::tr("Sketch Linear Pattern###Sketch Linear Pattern")\n'
     '                            : materializr::tr("Sketch Circular Pattern###Sketch Circular Pattern");'),
    ('ImGui::TextDisabled(materializr::touchMode()\n'
     '            ? "Drag the line to move it; drag the end dot to rotate."\n'
     '            : "Drag the line to move it; drag the end dot to rotate.");',
     'ImGui::TextDisabled("%s",\n'
     '            materializr::tr("Drag the line to move it; drag the end dot to rotate."));')])

edit("src/app/layout/LayoutCommon.cpp", [
    ('i == m_activeSession ? "(current)" : nullptr,',
     'i == m_activeSession ? materializr::tr("(current)") : nullptr,')])

edit("src/ui/WelcomeScreen.cpp", [
    ('ImGui::BeginPopupModal("Welcome###Welcome", &m_visible,',
     'ImGui::BeginPopupModal(materializr::tr("Welcome###Welcome"), &m_visible,')])

edit("src/ui/DrawingView.cpp", [], regexps=[(
    r'(case ProjectionDir::\w+:\s*return )"([^"]+)";', r'\1materializr::tr("\2");')])

# ---- catalogue merge (как в раундах 3-4) ----
PYFILE = "tools/i18n_catalogue.py"
py = open(PYFILE, encoding="utf-8").read()
if "RU_GAPS5" in py:
    print("catalogue: round-5 keys already registered")
else:
    def pylit(s):
        s = (s.replace("\\", "\\\\").replace('"', '\\"')
              .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
        return '"' + s + '"'
    block = ["\n# ---- Gap-fill round 5 (canvas, banners, inference labels) ----\n",
             "RU_GAPS5 = {\n"]
    for en, ru in sorted(RU5.items()):
        block.append("    %s: %s,\n" % (pylit(en), pylit(ru)))
    block.append("}\n\nfor _en, _ru in RU_GAPS5.items():\n"
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
    print("catalogue: %d round-5 keys registered" % len(RU5))

print("now run: python3 tools/i18n_catalogue.py")
