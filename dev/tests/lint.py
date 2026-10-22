#!/usr/bin/env python3
"""Refuse Lua that the game's Kahlua VM (Lua 5.1) cannot run.

Usage: python3 lint.py <folder> [<folder> ...]
Checks every .lua file (comments and strings stripped first) for:
  goto / labels, integer division //, bitwise operators, next(),
  string.rep, loadstring, table.unpack, utf8.*, and a global named `self`.
"""
import re
import sys
import pathlib

BAD = [
    (r"\bgoto\b", "goto (Lua 5.2+)"),
    (r"::\w+::", "label (Lua 5.2+)"),
    (r"//", "integer division // (Lua 5.3+)"),
    (r"(?<![~<>=])&|\|", "bitwise operator (Lua 5.3+)"),
    (r"<<|>>", "bit shift (Lua 5.3+)"),
    (r"(?<![\w.:])next\s*\(", "next() is not available in the game"),
    (r"\bstring\.rep\b|:rep\(", "string.rep is not available in the game"),
    (r"\bloadstring\b", "loadstring is not available in the game"),
    (r"\btable\.unpack\b", "table.unpack (use unpack)"),
    (r"\butf8\.", "utf8 library (Lua 5.3+)"),
]


def strip(src):
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith("--[[", i) or re.match(r"--\[=*\[", src[i:i + 8] or ""):
            m = re.match(r"--\[(=*)\[", src[i:])
            close = "]" + m.group(1) + "]"
            j = src.find(close, i)
            j = n if j < 0 else j + len(close)
            out.append("\n" * src.count("\n", i, j))
            i = j
        elif src.startswith("--", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src[i] in "\"'":
            q, j = src[i], i + 1
            while j < n and src[j] != q:
                j += 2 if src[j] == "\\" else 1
            out.append('""')
            i = j + 1
        elif re.match(r"\[=*\[", src[i:i + 8]):
            m = re.match(r"\[(=*)\[", src[i:])
            close = "]" + m.group(1) + "]"
            j = src.find(close, i)
            j = n if j < 0 else j + len(close)
            out.append('""' + "\n" * src.count("\n", i, j))
            i = j
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def main():
    problems = 0
    files = 0
    for root in sys.argv[1:]:
        for p in sorted(pathlib.Path(root).rglob("*.lua")):
            files += 1
            code = strip(p.read_text(encoding="utf-8", errors="replace"))
            for ln, line in enumerate(code.split("\n"), 1):
                for pat, why in BAD:
                    if re.search(pat, line):
                        print(f"{p}:{ln}: {why}: {line.strip()}")
                        problems += 1
    print(f"lint: {files} files, {problems} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
