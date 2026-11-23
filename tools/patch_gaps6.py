#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round 6: save prompt, primitive popup, Tools tab, bodies counters,
view cube, split labels, gizmo hint, user-axes lists."""
import sys, re
sys.path.insert(0, "tools")
from patch_gaps6_data import RU6

def rd(p): return open(p, encoding="utf-8").read()
def wr(p, s): open(p, "w", encoding="utf-8").write(s)

def rep(p, old, new):
    s = rd(p)
    if new in s:
        print(p, "уже переведено"); return
    if old not in s:
        print("!! NOT FOUND", p, repr(old[:60])); return
    wr(p, s.replace(old, new, 1)); print(p, "ok:", old[:40])

def rex(p, pat, r, cnt=0):
    s = rd(p); s2, k = re.subn(pat, r, s, count=cnt); wr(p, s2); print(p, "regex:", k)

def inc(p, rel):
    s = rd(p)
    if "i18n.h" in s: return
    i = s.index("#include"); j = s.index("\n", i)
    wr(p, s[:j+1] + '#include "%s"\n' % rel + s[j+1:]); print(p, "+include", rel)

# --- 1) Unsaved Changes ---
A = "src/app/Application.cpp"
rep(A, 'ImGui::OpenPopup("Unsaved Changes");',
    'ImGui::OpenPopup(materializr::tr("Unsaved Changes"));')
rep(A, 'ImGui::BeginPopupModal("Unsaved Changes"',
    'ImGui::BeginPopupModal(materializr::tr("Unsaved Changes").c_str()')
rep(A, "const char* prompt;", "std::string prompt;")
for lit in ["You have unsaved changes. Save before closing the project?",
            "You have unsaved changes. Save before closing this tab?",
            "You have unsaved changes. Save before opening another project?",
            "You have unsaved changes. Save before exiting?"]:
    rep(A, '"' + lit + '"', 'materializr::tr("' + lit + '")')
rep(A, 'ImGui::Text("%s", prompt);', 'ImGui::Text("%s", prompt.c_str());')

# --- 2) Primitive popup ---
D = "src/app/Application_Dialogs.cpp"
rep(D, "ImGui::Begin(titles[k], nullptr,",
    "ImGui::Begin(materializr::tr(titles[k]).c_str(), nullptr,")
rex(D, r'dimField\("([^"]+)"', r'dimField(materializr::tr("\1").c_str()')
rex(D, r'ImGui::Button\("Create"', r'ImGui::Button(materializr::tr("Create")')

# --- 3) Тренарник Linear/Circular: обернуть только если он аргумент Begin ---
s = rd(D)
m = re.search(r'\?\s*"Linear Pattern"\s*:\s*"Circular Pattern"', s)
if not m:
    print("ternary Linear/Circular: уже обёрнут")
else:
    i = m.start()
    a = max(s.rfind(";", 0, i), s.rfind("}", 0, i), s.rfind("{", 0, i)) + 1
    print("контекст тернарника:", s[a:m.end()+80].replace("\n", " | ")[:200])
    if "Begin(" in s[a:i]:
        rex(D, r'(\?\s*)"Linear Pattern"(\s*:\s*)"Circular Pattern"',
            r'\1materializr::tr("Linear Pattern").c_str()\2materializr::tr("Circular Pattern").c_str()', 1)
    else:
        print("!! ternary не в аргументе Begin - не трогаю, пришли контекст выше")

# --- 4) Списки осей (user): оборачиваем источник массива ---
OLD_ARR = 'const char* userLabels[3] = {"X (user)", "Y (user)", "Z (user, floor-up)"};'
NEW_ARR = ('const std::string userLabelsTr[3] = {materializr::tr("X (user)"), materializr::tr("Y (user)"),\n'
           '                                    materializr::tr("Z (user, floor-up)")};\n'
           'const char* userLabels[3] = {userLabelsTr[0].c_str(), userLabelsTr[1].c_str(),\n'
           '                             userLabelsTr[2].c_str()};')
s = rd(D)
if 'userLabelsTr' in s:
    print("оси user: уже переведены")
elif OLD_ARR not in s:
    print("!! NOT FOUND массив userLabels в Application_Dialogs.cpp")
else:
    wr(D, s.replace(OLD_ARR, NEW_ARR, 1)); print("оси user: массивы обёрнуты")
rep(D, 'ImGui::Selectable(materializr::tr(userLabels[i]), sel)',
    'ImGui::Selectable(userLabels[i], sel)')

# --- 5) Вкладка Tools ---
T = "src/ui/Toolbar.cpp"
rep(T, 'ImGui::Begin("Tools", nullptr, ImGuiWindowFlags_NoCollapse);',
    'ImGui::Begin(materializr::tr("Tools").c_str(), nullptr, ImGuiWindowFlags_NoCollapse);')
inc(T, "../i18n.h")

# --- 6) Счётчики тел ---
I = "src/ui/ItemsPanel.cpp"
rep(I, 'std::snprintf(countText, sizeof(countText), "Bodies: %d", m_document->bodyCount());',
    'std::snprintf(countText, sizeof(countText), materializr::tr("Bodies: %d").c_str(), m_document->bodyCount());')
V = "src/ui/VersionPanel.cpp"
rep(V, 'std::snprintf(bodiesBuf, sizeof(bodiesBuf), "Bodies: %d", entry.bodyCount);',
    'std::snprintf(bodiesBuf, sizeof(bodiesBuf), materializr::tr("Bodies: %d").c_str(), entry.bodyCount);')

# --- 7) SplitController: left/right и компания ---
SC = "src/app/SplitController.cpp"
rep(SC,
    'const char* axisSplitDescription(int a) {\n'
    '    return a == 0 ? "left / right"\n'
    '         : a == 1 ? "front / back"\n'
    '                  : "top / bottom";\n'
    '}',
    'std::string axisSplitDescription(int a) {\n'
    '    return a == 0 ? materializr::tr("left / right")\n'
    '         : a == 1 ? materializr::tr("front / back")\n'
    '                  : materializr::tr("top / bottom");\n'
    '}')
inc(SC, "../i18n.h")

# --- 8) ViewCube: подписи Top/Bottom (буквы F/B/L/R не трогаем) ---
VC = "src/viewport/ViewCube.cpp"
rep(VC, "ImVec2 ts = ImGui::CalcTextSize(f.label);",
    "ImVec2 ts = ImGui::CalcTextSize(materializr::tr(f.label).c_str());")
rep(VC, "ink(255), f.label);",
    "ink(255), materializr::tr(f.label).c_str());")
inc(VC, "../i18n.h")

# --- 9) Подсказка гизмо ---
rep("src/app/Application_Viewport.cpp",
    '"Arrows: Move | Rings: Rotate | Cubes: Scale");',
    'materializr::tr("Arrows: Move | Rings: Rotate | Cubes: Scale"));')

# --- 10) Слияние каталога ---
PYFILE = "tools/i18n_catalogue.py"
py = rd(PYFILE)
if "RU_GAPS6" in py:
    print("catalogue: round-6 keys already registered")
else:
    def pylit(x):
        x = (x.replace("\\", "\\\\").replace('"', '\\"')
              .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
        return '"' + x + '"'
    block = ["\n# ---- Gap-fill round 6 (dialogs, view cube, counters) ----\n",
             "RU_GAPS6 = {\n"]
    for en, ru in sorted(RU6.items()):
        block.append("    %s: %s,\n" % (pylit(en), pylit(ru)))
    block.append("}\n\n"
                 'for _en, _ru in RU_GAPS6.items():\n'
                 '    for _entry in CAT:\n'
                 '        if _entry[0] == _en:\n'
                 '            if not _entry[1].get("ru"):\n'
                 '                _entry[1]["ru"] = _ru\n'
                 '            break\n'
                 '    else:\n'
                 '        CAT.append((_en, {"es":"", "pt":"", "fr":"", '
                 '"de":"", "it":"", "ru":_ru}))\n')
    anchor = py.index("def cstr(")
    wr(PYFILE, py[:anchor] + "".join(block) + "\n" + py[anchor:])
    print("catalogue: %d round-6 keys registered" % len(RU6))

# --- 11) Разведка остатков (для round 6b) ---
import subprocess
def sh(cmd):
    print("### " + cmd)
    print(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout)
sh("sed -n '5655,5690p' src/app/Application_Dialogs.cpp")
sh("sed -n '4805,4830p' src/app/Application_Dialogs.cpp")
sh("grep -rn 'interactiveOpName' src --include=*.cpp | grep -v InteractiveOp.cpp | head -8")
sh("grep -rn 'registerToolbarButton' src/app src/ui --include=*.cpp --include=*.h | head -8")
