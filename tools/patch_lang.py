#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-select the UI language from the system locale at first launch.

Edits:
  src/i18n.h            - declare systemLanguageIndex()
  src/i18n.cpp          - implement it: SDL_GetPreferredLocales on SDL 2.0.14+,
                          Android system-property fallback for older SDL
  src/app/Application.* - adopt the detected language when the user has never
                          chosen one; comments updated to match.
"""
import sys, glob

def patch_file(path, repl, marker):
    src = open(path, encoding="utf-8").read()
    if marker in src:
        print("%s: already patched" % path)
        return
    for old, new in repl:
        if new in src:
            continue
        if old not in src:
            print("!! NOT FOUND in %s: %r" % (path, old[:70])); sys.exit(1)
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("%s: patched" % path)

# --- 1. i18n.h -------------------------------------------------------------
patch_file("src/i18n.h", [(
    "void setLanguage(Lang l);",
    "void setLanguage(Lang l);\n"
    "// Index of the system's preferred UI language (Lang order), or -1 when\n"
    "// the platform cannot tell. Called once at startup, before the user has\n"
    "// ever chosen, to pre-select the language instead of asking.\n"
    "int systemLanguageIndex();"
)], "systemLanguageIndex")

# --- 2. i18n.cpp -----------------------------------------------------------
INCLUDES = (
    "#include <vector>\n"
    "\n"
    "#include <SDL_version.h>\n"
    "#if SDL_VERSION_ATLEAST(2, 0, 14)\n"
    "#include <SDL_locale.h>\n"
    "#endif\n"
    "#if defined(__ANDROID__)\n"
    "#include <sys/system_properties.h>\n"
    "#endif\n"
)
IMPL = (
    "\n"
    "// ---- system language detection -------------------------------------------\n"
    "namespace {\n"
    "\n"
    "// Lang order (English 0 ... Russian 6); codes are what OS locales report.\n"
    "const char* kLangCodes[] = {\"en\", \"es\", \"pt\", \"fr\", \"de\", \"it\", \"ru\"};\n"
    "\n"
    "char lc(char c) { return (c >= 'A' && c <= 'Z') ? char(c - 'A' + 'a') : c; }\n"
    "bool codeEq(const char* a, const char* b) {\n"
    "    while (*a && *b) {\n"
    "        if (lc(*a) != lc(*b)) return false;\n"
    "        ++a; ++b;\n"
    "    }\n"
    "    return *a == 0 && *b == 0;\n"
    "}\n"
    "\n"
    "} // namespace\n"
    "\n"
    "int languageIndexFromCode(const char* code) {\n"
    "    if (!code || !code[0]) return -1;\n"
    "    for (int i = 0; i < static_cast<int>(Lang::COUNT); ++i) {\n"
    "        if (i < static_cast<int>(sizeof(kLangCodes) / sizeof(kLangCodes[0])) &&\n"
    "            codeEq(code, kLangCodes[i]))\n"
    "            return i;\n"
    "    }\n"
    "    return -1;\n"
    "}\n"
    "\n"
    "int systemLanguageIndex() {\n"
    "#if SDL_VERSION_ATLEAST(2, 0, 14)\n"
    "    // SDL asks the OS for the user's preferred locales (Android, iOS,\n"
    "    // Windows, macOS); NULL when it cannot tell.\n"
    "    if (SDL_Locale* locs = SDL_GetPreferredLocales()) {\n"
    "        int found = -1;\n"
    "        for (SDL_Locale* l = locs; found < 0 && l && l->language; ++l)\n"
    "            found = languageIndexFromCode(l->language);\n"
    "        SDL_free(locs);\n"
    "        if (found >= 0) return found;\n"
    "    }\n"
    "#endif\n"
    "#if defined(__ANDROID__)\n"
    "    // Fallback for older SDL: read the system property directly. The value\n"
    "    // looks like \"ru-RU\"; the part before '-' is what we match.\n"
    "    char buf[PROP_VALUE_MAX] = {0};\n"
    "    for (const char* name : {\"persist.sys.locale\", \"ro.product.locale\"})\n"
    "        if (__system_property_get(name, buf) > 0 && buf[0]) break;\n"
    "    if (buf[0]) {\n"
    "        std::string code(buf);\n"
    "        const std::size_t dash = code.find('-');\n"
    "        if (dash != std::string::npos) code = code.substr(0, dash);\n"
    "        return languageIndexFromCode(code.c_str());\n"
    "    }\n"
    "#endif\n"
    "    return -1;\n"
    "}\n"
    "\n"
)
patch_file("src/i18n.cpp", [
    ("#include <vector>\n", INCLUDES),
    ("} // namespace", "} // namespace" + IMPL),
], "systemLanguageIndex")

# --- 3. Application.cpp ----------------------------------------------------
patch_file("src/app/Application.cpp", [
    ("    // UI language - also live. -1 means the user has never chosen, which the\n"
     "    // setup wizard turns into its opening question; until then, English.\n"
     "    m_language = s.language;\n"
     "    setLanguage((s.language > 0 && s.language < languageCount())\n"
     "                    ? static_cast<Lang>(s.language)\n"
     "                    : Lang::English);",
     "    // UI language - also live. -1 means the user has never chosen: adopt\n"
     "    // the system language (the tour only asks when the OS cannot tell);\n"
     "    // English stays the pass-through fallback.\n"
     "    m_language = s.language;\n"
     "    if (m_language < 0) {\n"
     "        const int sysLang = materializr::systemLanguageIndex();\n"
     "        if (sysLang >= 0) m_language = sysLang;\n"
     "    }\n"
     "    setLanguage((m_language > 0 && m_language < languageCount())\n"
     "                    ? static_cast<Lang>(m_language)\n"
     "                    : Lang::English);"),
], "systemLanguageIndex")

# --- 4. Application.h ------------------------------------------------------
patch_file("src/app/Application.h", [(
    "    // UI language index, mirroring materializr::Lang. -1 = never chosen, which\n"
    "    // is what makes the setup wizard open with the language question.\n"
    "    int m_language = -1;",
    "    // UI language index, mirroring materializr::Lang. -1 = never chosen; at\n"
    "    // startup the loader replaces it with the system language when the OS\n"
    "    // can tell, so the tour's language page opens only if detection failed.\n"
    "    int m_language = -1;"
)], "system language when the OS")

# --- sanity: the -1 sentinel must be the struct default --------------------
for f in glob.glob("src/app/*.h"):
    for n, line in enumerate(open(f, encoding="utf-8"), 1):
        if "language" in line and ("int " in line or "short " in line) and "=" in line:
            print("default check %s:%d: %s" % (f, n, line.strip()))

print("done - build and check the tour skips the language page on a ru device")
