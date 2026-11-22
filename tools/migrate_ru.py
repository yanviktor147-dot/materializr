#!/usr/bin/env python3
"""Migrate the hand-added kRuCatalogue into tools/i18n_catalogue.py (v3)."""
import re

HEADER = "src/i18n_catalogue.h"
PYFILE = "tools/i18n_catalogue.py"

# The literal body may contain \xNN"" sequences (cstr() escaping), hence
# the explicit "" alternative.
ROW = re.compile(
    r'^\s*\{\s*("(?:[^"\\]|\\.|"")*")\s*,\s*("(?:[^"\\]|\\.|"")*")\s*\},?\s*(?://.*)?$',
    re.M)

def unesc(s):
    """Decode a C string literal BODY (no surrounding quotes)."""
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            n = s[i + 1]
            if n == "x":
                j, hx = i + 2, ""
                while j < len(s) and s[j] in "0123456789abcdefABCDEF" and len(hx) < 2:
                    hx += s[j]; j += 1
                out.append(int(hx, 16))
                if s[j:j + 2] == '""': j += 2
                i = j
            else:
                out += {"n": "\n", "t": "\t", "r": "\r",
                        '"': '"', "\\": "\\"}[n].encode("utf-8")
                i += 2
        else:
            out += c.encode("utf-8"); i += 1
    return out.decode("utf-8")

def pylit(s):
    s = (s.replace("\\", "\\\\").replace('"', '\\"')
          .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
    return '"' + s + '"'

src = open(HEADER, encoding="utf-8").read()
a = src.index("kRuCatalogue[] = {")
b = src.index("kRuCount", a)
rows = ROW.findall(src[a:b])
print("raw rows matched:", len(rows))
ru = {unesc(en[1:-1]): unesc(rv[1:-1]) for en, rv in rows}
print("extracted %d russian entries" % len(ru))

py = open(PYFILE, encoding="utf-8").read()
assert '"ru"' not in py, "ru already present? restore the file first"
py = py.replace('LANGS = ["es", "pt", "fr", "de", "it"]',
                'LANGS = ["es", "pt", "fr", "de", "it", "ru"]', 1)
py = py.replace('"de":"Deutsch", "it":"Italiano"}',
                '"de":"Deutsch", "it":"Italiano", "ru":"Русский"}', 1)
py = py.replace('"de":"German", "it":"Italian"}',
                '"de":"German", "it":"Italian", "ru":"Russian"}', 1)

block = ["\n# ---- Russian (migrated from hand-added kRuCatalogue) -------------\n",
         "RU = {\n"]
for en, rv in sorted(ru.items()):
    block.append("    %s: %s,\n" % (pylit(en), pylit(rv)))
block.append("}\n\n")
block.append("for en, tr in CAT:\n    tr[\"ru\"] = RU.get(en, \"\")\n")
anchor = py.index("def cstr(")
py = py[:anchor] + "".join(block) + "\n" + py[anchor:]

open(PYFILE, "w", encoding="utf-8").write(py)
print("patched %s -- now run: python3 tools/i18n_catalogue.py" % PYFILE)
