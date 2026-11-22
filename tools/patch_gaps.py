#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrap remaining hardcoded UI strings in tr(); add RU keys (v2, idempotent)."""
import re, sys
sys.path.insert(0, "tools")
from patch_gaps_data import GAPS

def patch(path, pairs):
    src = open(path, encoding="utf-8").read()
    dirty = False
    for old, new in pairs:
        if new in src:
            continue                      # already applied by an earlier run
        if old not in src:
            print("!! NOT FOUND in %s: %r" % (path, old[:70])); sys.exit(1)
        src = src.replace(old, new, 1); dirty = True
    if dirty:
        open(path, "w", encoding="utf-8").write(src)
    print("patched", path)

def ensure_include(path, include, probe):
    src = open(path, encoding="utf-8").read()
    if probe in src: return
    i = src.index("#include"); j = src.index("\n", i) + 1
    src = src[:j] + include + "\n" + src[j:]
    open(path, "w", encoding="utf-8").write(src)
    print("added %s to %s" % (include, path))

TUT = "src/plugins/TutorialPlugin.cpp"

def remove_disclaimer():
    """Delete the now-false 'some longer help text is still English' block."""
    src = open(TUT, encoding="utf-8").read()
    i = src.find("// Honest about")
    if i == -1:
        print("disclaimer: already gone" if "still English" not in src
              else "!! comment gone, but 'still English' text still present?")
        return
    start = src.rfind("\n", 0, i) + 1          # line start of the comment
    j = src.find("ImGui::PopTextWrapPos();", i)
    if j == -1:
        print("!! PopTextWrapPos not found after the comment"); sys.exit(1)
    end = src.find("\n", j) + 1                # end of that line
    print("removing disclaimer block:")
    print(src[start:end].rstrip())
    open(TUT, "w", encoding="utf-8").write(src[:start] + src[end:])

patch(TUT, [
    ("ImGui::SeparatorText(s.title);",
     "ImGui::SeparatorText(materializr::tr(s.title));"),
    ("ImGui::TextUnformatted(s.body);",
     "ImGui::TextUnformatted(materializr::tr(s.body));"),
    ('ImGui::TextWrapped(materializr::tr("In this layout:  %s"), s.where[li]);',
     'ImGui::TextWrapped(materializr::tr("In this layout:  %s"),\n                    materializr::tr(s.where[li]));'),
    ('{ guide("Touch:", s.touch, true);  guide("Mouse:", s.mouse, false); }',
     '{ guide(materializr::tr("Touch:"), materializr::tr(s.touch), true);  guide(materializr::tr("Mouse:"), materializr::tr(s.mouse), false); }'),
    ('{ guide("Mouse:", s.mouse, true);  guide("Touch:", s.touch, false); }',
     '{ guide(materializr::tr("Mouse:"), materializr::tr(s.mouse), true);  guide(materializr::tr("Touch:"), materializr::tr(s.touch), false); }'),
    ('if (ImGui::Button(last ? "Finish" : "Next", uiSz(80, 0))) {',
     'if (ImGui::Button(last ? materializr::tr("Finish") : materializr::tr("Next"), uiSz(80, 0))) {'),
    ('if (ImGui::Button(last ? "Close" : "Skip", uiSz(80, 0))) close();',
     'if (ImGui::Button(last ? materializr::tr("Close") : materializr::tr("Skip"), uiSz(80, 0))) close();'),
    ('if (ImGui::Begin("Getting Started###Tutorial", &keepOpen,',
     'const std::string tutTitle = std::string(materializr::tr("Getting Started")) + "###Tutorial";\n    if (ImGui::Begin(tutTitle.c_str(), &keepOpen,'),
    ("ImVec2 blurbSz = ImGui::CalcTextSize(kLayouts[i].blurb, nullptr,",
     "ImVec2 blurbSz = ImGui::CalcTextSize(materializr::tr(kLayouts[i].blurb), nullptr,"),
    ("kLayouts[i].blurb, nullptr, wrapW);",
     "materializr::tr(kLayouts[i].blurb), nullptr, wrapW);"),
    ("dl->AddText(txt, ImGui::GetColorU32(ImGuiCol_Text), kLayouts[i].name);",
     "dl->AddText(txt, ImGui::GetColorU32(ImGuiCol_Text), materializr::tr(kLayouts[i].name));"),
])
remove_disclaimer()

patch("src/ui/HelpPanel.cpp", [
    ('ImGui::TextColored(materializr::accentText(), "%s", title);',
     'ImGui::TextColored(materializr::accentText(), "%s", materializr::tr(title));'),
    ('ImGui::TextWrapped("%s", body);',
     'ImGui::TextWrapped("%s", materializr::tr(body));'),
    ('if (!ImGui::Begin("User Guide", &m_visible)) { ImGui::End(); return; }',
     'if (!ImGui::Begin(materializr::tr("User Guide"), &m_visible)) { ImGui::End(); return; }'),
    ("Scale snaps to 1%% and shows", "Scale snaps to 1% and shows"),
])

patch("src/ui/LandingPage.cpp", [
    ('        const char* openLbl = ICON_IC_FOLDER "  Open File...";\n'
     '        const char* helpLbl = ICON_IC_HELP_CIRCLE "  Help";\n'
     '        const char* gearLbl = ICON_IC_SETTINGS "  Settings";',
     '        const std::string openLblS = std::string(ICON_IC_FOLDER) + "  " + materializr::tr("Open File...");\n'
     '        const std::string helpLblS = std::string(ICON_IC_HELP_CIRCLE) + "  " + materializr::tr("Help");\n'
     '        const std::string gearLblS = std::string(ICON_IC_SETTINGS) + "  " + materializr::tr("Settings");\n'
     '        const char* openLbl = openLblS.c_str();\n'
     '        const char* helpLbl = helpLblS.c_str();\n'
     '        const char* gearLbl = gearLblS.c_str();'),
    ('tile("new", "New Project", 0, ICON_IC_PLUS, tileW, previewH,',
     'tile("new", materializr::tr("New Project"), 0, ICON_IC_PLUS, tileW,\n             previewH,'),
    ('"Start an empty project", false)',
     'materializr::tr("Start an empty project"), false)'),
])

ensure_include("src/io/FileDialogs.cpp", '#include "../i18n.h"', "i18n.h")
patch("src/io/FileDialogs.cpp", [
    ('title.empty() ? (isSave ? "Save File" : "Open File") : title;',
     'title.empty() ? (isSave ? materializr::tr("Save File") : materializr::tr("Open File")) : title;'),
])

ensure_include("src/app/Application_Dialogs.cpp", '#include "../i18n.h"', "i18n.h")
patch("src/app/Application_Dialogs.cpp", [
    ('ImGui::Begin("Settings", &m_showSettings)',
     'ImGui::Begin(materializr::tr("Settings"), &m_showSettings)'),
])

# ---- catalogue: add gap keys with RU (existing non-empty RU kept) ----
PYFILE = "tools/i18n_catalogue.py"
py = open(PYFILE, encoding="utf-8").read()
if "RU_GAPS" in py:
    print("catalogue: gap keys already registered")
else:
    def pylit(s):
        s = (s.replace("\\", "\\\\").replace('"', '\\"')
              .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
        return '"' + s + '"'
    block = ["\n# ---- Gap-fill keys (hardcoded strings wrapped in tr()) ----\n",
             "RU_GAPS = {\n"]
    for en, ru in sorted(GAPS):
        block.append("    %s: %s,\n" % (pylit(en), pylit(ru)))
    block.append("}\n\nfor _en, _ru in RU_GAPS.items():\n"
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
    print("catalogue: %d gap keys registered" % len(GAPS))
print("now run: python3 tools/i18n_catalogue.py")
