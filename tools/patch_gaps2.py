#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round 2: welcome dialog, panel titles, status bar, legend, multi-select."""
import sys
sys.path.insert(0, "tools")
from patch_gaps2_data import GAPS2

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

def ensure_include(path, include, probe):
    src = open(path, encoding="utf-8").read()
    if probe in src: return
    i = src.index("#include"); j = src.index("\n", i) + 1
    src = src[:j] + include + "\n" + src[j:]
    open(path, "w", encoding="utf-8").write(src)
    print("added %s to %s" % (include, path))

# ---- Welcome dialog ----
W = "src/ui/WelcomeScreen.cpp"
patch(W, [
    ('if (!ImGui::IsPopupOpen("Welcome")) ImGui::OpenPopup("Welcome");',
     'if (!ImGui::IsPopupOpen("Welcome###Welcome")) ImGui::OpenPopup("Welcome###Welcome");'),
    ('if (ImGui::BeginPopupModal("Welcome", &m_visible,',
     'if (ImGui::BeginPopupModal("Welcome###Welcome", &m_visible,'),
    ('std::string verLine = std::string("Version ") + MATERIALIZR_VERSION;',
     'std::string verLine = materializr::trFormat("Version %s", MATERIALIZR_VERSION);'),
    ('const char* already = "I already support - don\'t show this again";',
     'const std::string alreadyS =\n'
     '            materializr::tr("I already support - don\'t show this again");\n'
     '        const char* already = alreadyS.c_str();'),
    ('if (ImGui::Button(working ? "Contacting the App Store..." : "Support Materializr",',
     'if (ImGui::Button(working ? materializr::tr("Contacting the App Store...")\n'
     '                                  : materializr::tr("Support Materializr"),'),
    ('const char* restore = "Already a supporter? Restore purchase";',
     'const std::string restoreS =\n'
     '            materializr::tr("Already a supporter? Restore purchase");\n'
     '        const char* restore = restoreS.c_str();'),
])

# ---- docked panel titles (### suffix keeps the ID stable) ----
patch("src/ui/HistoryPanel.cpp", [
    ('ImGui::Begin("History", nullptr, ImGuiWindowFlags_NoCollapse);',
     'ImGui::Begin(materializr::tr("History###History"), nullptr,\n'
     '                 ImGuiWindowFlags_NoCollapse);'),
])
patch("src/ui/ItemsPanel.cpp", [
    ('ImGui::Begin("Items", nullptr, ImGuiWindowFlags_NoCollapse);',
     'ImGui::Begin(materializr::tr("Items###Items"), nullptr,\n'
     '                 ImGuiWindowFlags_NoCollapse);'),
])
patch("src/ui/PropertiesPanel.cpp", [
    ('ImGui::Begin("Properties", nullptr, ImGuiWindowFlags_NoCollapse);',
     'ImGui::Begin(materializr::tr("Properties###Properties"), nullptr,\n'
     '                 ImGuiWindowFlags_NoCollapse);'),
])
patch("src/app/Application_Dialogs.cpp", [
    ('ImGui::Begin("Interactions", nullptr, ImGuiWindowFlags_NoCollapse);',
     'ImGui::Begin(materializr::tr("Interactions###Interactions"), nullptr,\n'
     '                 ImGuiWindowFlags_NoCollapse);'),
    # legend: wrap the shared row() once - every hint line follows
    ('    auto row = [touchRagged](const char* action, const char* keys) {\n'
     '        ImGui::TextUnformatted(action);\n'
     '        if (touchRagged) ImGui::SameLine();\n'
     '        else             ImGui::SameLine(120.0f);\n'
     '        ImGui::TextColored(materializr::accentText(), "%s", keys);\n'
     '    };',
     '    auto row = [touchRagged](const char* action, const char* keys) {\n'
     '        ImGui::TextUnformatted(materializr::tr(action));\n'
     '        if (touchRagged) ImGui::SameLine();\n'
     '        else             ImGui::SameLine(120.0f);\n'
     '        ImGui::TextColored(materializr::accentText(), "%s",\n'
     '                           materializr::tr(keys));\n'
     '    };'),
])
ensure_include("src/ui/DrawingView.cpp", '#include "../i18n.h"', "i18n.h")
patch("src/ui/DrawingView.cpp", [
    ('ImGui::Begin("2D Drawing");',
     'ImGui::Begin(materializr::tr("2D Drawing###2D Drawing"));'),
])

# ---- status bar ----
patch("src/ui/StatusBar.cpp", [
    ('m_projectName.empty() ? "New project"',
     'm_projectName.empty() ? materializr::tr("New project")'),
    ('std::snprintf(bodiesText, sizeof(bodiesText), "Bodies: %d", bodyCount);',
     'std::snprintf(bodiesText, sizeof(bodiesText),\n'
     '                      materializr::tr("Bodies: %d"), bodyCount);'),
    ('std::snprintf(toolText, sizeof(toolText), "Tool: %s", m_currentTool.c_str());',
     'std::snprintf(toolText, sizeof(toolText), materializr::tr("Tool: %s"),\n'
     '                      materializr::tr(m_currentTool.c_str()));'),
])

# ---- tab / session fallback names ----
LC = "src/app/layout/LayoutCommon.cpp"
patch(LC, [
    ('if (i >= m_sessions.size()) return "Untitled";',
     'if (i >= m_sessions.size()) return materializr::tr("Untitled");'),
    ('    return "Untitled";',
     '    return materializr::tr("Untitled");'),
])

# ---- default project name ----
patch("src/app/Application.cpp", [
    ('if (m_currentProjectPath.empty()) return "New project";',
     'if (m_currentProjectPath.empty()) return materializr::tr("New project");'),
])

# ---- multi-select toggle ----
ensure_include("src/app/Application_Viewport.cpp", '#include "../i18n.h"', "i18n.h")
patch("src/app/Application_Viewport.cpp", [
    ('if (wideButton(m_multiSelectToggle ? "Multi-Select: On" : "Multi-Select: Off"))',
     'if (wideButton(m_multiSelectToggle ? materializr::tr("Multi-Select: On")\n'
     '                                   : materializr::tr("Multi-Select: Off")))'),
])

# ---- catalogue merge (keeps existing non-empty RU) ----
PYFILE = "tools/i18n_catalogue.py"
py = open(PYFILE, encoding="utf-8").read()
if "RU_GAPS2" in py:
    print("catalogue: round-2 keys already registered")
else:
    def pylit(s):
        s = (s.replace("\\", "\\\\").replace('"', '\\"')
              .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
        return '"' + s + '"'
    block = ["\n# ---- Gap-fill round 2 ----\n", "RU_GAPS2 = {\n"]
    for en, ru in sorted(GAPS2):
        block.append("    %s: %s,\n" % (pylit(en), pylit(ru)))
    block.append("}\n\nfor _en, _ru in RU_GAPS2.items():\n"
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
    print("catalogue: %d round-2 keys registered" % len(GAPS2))
print("now run: python3 tools/i18n_catalogue.py")
