#!/usr/bin/env python3
"""Check every segment's cues.json against STYLE.md: structure, length, banned words, spellings.

    python3 curriculum/video/lint.py          # all segments
    python3 curriculum/video/lint.py S07 S08  # some

Exit status is 1 if anything is flagged. Warnings (W) are judgement calls; errors (E) break the
series' shape and should be fixed before rendering.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS_MIN, WORDS_MAX, CUE_MAX = 480, 680, 120
BANNED = {r"\bawesome\b": "hype word", r"\bsuper\b": "hype word", r"\bepic\b": "hype word", r"\bcool\b": "hype word",
          r"\bguys\b": "talks down", r"\bkids?\b": "talks down", r"\bkiddos?\b": "talks down",
          r"\bboys and girls\b": "talks down", r"you might not know": "talks down",
          r"!": "no exclamation marks", r";": "no semicolons in narration", r"—": "no em dashes in narration",
          r"\bengine\b": "say motor", r"\bcentre\b": "US spelling: center", r"\bcalibre\b": "US spelling: caliber",
          r"\bhigh-power\b": "high power, no hyphen", r"\bOpen Rocket\b": "OpenRocket", r"\bAlpha 3\b": "Alpha III",
          r"\bBR1\b": "BR-1", r"\bnewton[- ]seconds?\b": "Newton-seconds, capital N", r"\bmm\b": "spell out millimetres in narration",
          r"\bNs\b": "N·s on slides, Newton-seconds spoken"}
NARRATOR_WE = re.compile(r"\b(we|we're|we've|let's|our|us)\b", re.I)


def words(s):
    return len(s.split())


def lint(seg):
    p = os.path.join(HERE, seg, "cues.json")
    spec = json.load(open(p, encoding="utf-8"))
    meta, cues = spec["meta"], spec["cues"]
    out = []
    E = lambda m: out.append(("E", m)); Wn = lambda m: out.append(("W", m))
    num = int(re.sub(r"\D", "", seg))
    if meta.get("eyebrow") != f"Segment {num}  ·  While the epoxy cures":
        E(f"eyebrow should be 'Segment {num}  ·  While the epoxy cures', is {meta.get('eyebrow')!r}")
    if meta.get("footer") != "Minerva BR-1 build day  ·  Georgia Wing High Power Rocketry":
        E("footer differs from S06")
    for k in ("title", "description", "tags"):
        if not meta.get(k):
            E(f"meta.{k} missing")
    if not 8 <= len(cues) <= 11:
        Wn(f"{len(cues)} cues; STYLE says 8 to 11")
    if cues[0]["type"] != "title":
        E("first cue is not a title")
    if cues[-1]["type"] != "close":
        E("last cue is not a close")
    pauses = [i for i, c in enumerate(cues) if c["type"] == "pause"]
    if len(pauses) != 1:
        E(f"{len(pauses)} pause cues; need exactly one")
    elif pauses[0] + 1 >= len(cues) or cues[pauses[0] + 1]["type"] != "answer":
        E("the cue after the pause is not an answer")
    first = cues[0].get("say", "")
    if not re.match(rf"Segment {num_word(num)}[.,]", first, re.I) and not re.match(rf"Segment {num}[.,]", first):
        Wn(f"title narration should open 'Segment {num_word(num)}.'; opens {first[:40]!r}")
    if "by the end of this you will be able to" not in first.lower():
        Wn("title narration should say 'By the end of this you will be able to ...'")
    last = cues[-1].get("say", "")
    if not last.startswith("The one thing to remember"):
        Wn("close narration should start 'The one thing to remember.'")
    total = 0
    for i, c in enumerate(cues, 1):
        say = c.get("say", "")
        if c["type"] == "pause":
            if say:
                E(f"cue {i}: pause cue must not have narration")
            if not c.get("question"):
                E(f"cue {i}: pause cue needs a question")
            continue
        if not say:
            E(f"cue {i} ({c['type']}): no narration")
        n = words(say); total += n
        if n > CUE_MAX:
            Wn(f"cue {i} ({c['type']}): {n} words, over {CUE_MAX}")
        for pat, why in BANNED.items():
            if re.search(pat, say):
                Wn(f"cue {i}: {why} ({pat!r})")
        for mt in NARRATOR_WE.finditer(say):
            Wn(f"cue {i}: narrator says {mt.group(0)!r}; use 'you' or 'the program'"); break
        if c["type"] == "answer" and not c.get("text"):
            E(f"cue {i}: answer cue needs text")
        for ln in c.get("lines", []):
            if words(ln) > 9:
                Wn(f"cue {i}: bullet line over 8 words: {ln!r}")
        if len(c.get("lines", [])) > 3:
            Wn(f"cue {i}: more than three bullet lines")
        sents = [s for s in re.split(r"[.!?]+\s", say) if s.strip()]
        if sents:
            avg = sum(words(s) for s in sents) / len(sents)
            if avg > 18:
                Wn(f"cue {i}: average sentence {avg:.0f} words; aim under 15")
    if total < WORDS_MIN:
        Wn(f"{total} narration words, under {WORDS_MIN}")
    if total > WORDS_MAX:
        E(f"{total} narration words, over {WORDS_MAX}")
    return total, out


def num_word(n):
    return ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"][n]


if __name__ == "__main__":
    segs = [a for a in sys.argv[1:] if not a.startswith("-")] or sorted(
        d for d in os.listdir(HERE) if re.fullmatch(r"S\d+", d) and os.path.exists(os.path.join(HERE, d, "cues.json")))
    bad = False
    for seg in segs:
        total, out = lint(seg)
        print(f"{seg}: {total} words, {len([o for o in out if o[0]=='E'])} errors, {len([o for o in out if o[0]=='W'])} warnings")
        for lvl, msg in out:
            print(f"   {lvl}  {msg}")
        bad |= any(l == "E" for l, _ in out)
    sys.exit(1 if bad else 0)
