#!/usr/bin/env python3
"""Series-wide spelling and number-form normalization for cue files, applied in place.

    python3 curriculum/video/normalize.py S01 S02 ...   (or no args: every segment)

US spelling everywhere (the guide says center, caliber, meter). In narration ("say") a segment is
referred to in words, "Segment six", since numbers are spoken in words; slide text keeps digits.
Prints which files changed. Safe to run repeatedly.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
SPELL = [(r"\bmetres\b", "meters"), (r"\bmetre\b", "meter"), (r"\bmillimetres\b", "millimeters"), (r"\bmillimetre\b", "millimeter"),
         (r"\bcentimetres\b", "centimeters"), (r"\bcentimetre\b", "centimeter"), (r"\bkilometres\b", "kilometers"),
         (r"\brecognise\b", "recognize"), (r"\brecognised\b", "recognized"), (r"\borganisations?\b", lambda m: m.group(0).replace("s", "z", 1) if False else m.group(0).replace("isation", "ization")),
         (r"\bcentre\b", "center"), (r"\bcalibre\b", "caliber"), (r"\bfibreglass\b", "fiberglass"), (r"\bgrey\b", "gray"),
         (r"\bMetres\b", "Meters"), (r"\bMetre\b", "Meter")]


def fix_text(s, say=False):
    for pat, rep in SPELL:
        s = re.sub(pat, rep, s)
    if say:
        s = re.sub(r"\bSegment (\d{1,2})\b", lambda m: "Segment " + WORDS[int(m.group(1))] if int(m.group(1)) <= 12 else m.group(0), s)
        s = re.sub(r"\bSegments (\d{1,2}), (\d{1,2}) and (\d{1,2})\b",
                   lambda m: "Segments " + ", ".join(WORDS[int(x)] for x in m.groups()[:2]) + " and " + WORDS[int(m.group(3))], s)
    return s


def walk(x, say_key=False):
    if isinstance(x, dict):
        return {k: walk(v, say_key=(k == "say")) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v, say_key) for v in x]
    if isinstance(x, str):
        return fix_text(x, say=say_key)
    return x


if __name__ == "__main__":
    segs = sys.argv[1:] or sorted(d for d in os.listdir(HERE) if re.fullmatch(r"S\d+", d))
    for seg in segs:
        p = os.path.join(HERE, seg, "cues.json")
        if not os.path.exists(p):
            continue
        raw = open(p, encoding="utf-8").read()
        spec = json.loads(raw)
        new = walk(spec)
        out = json.dumps(new, indent=2, ensure_ascii=False) + "\n"
        if json.dumps(new, ensure_ascii=False) != json.dumps(spec, ensure_ascii=False):
            open(p, "w", encoding="utf-8").write(out)
            print(seg, "changed")
        else:
            print(seg, "unchanged")
