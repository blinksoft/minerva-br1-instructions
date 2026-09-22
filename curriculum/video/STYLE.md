# Voice and style for the segment videos

Every segment is written by a different hand and read by one of two synthetic voices, so this is the
contract that makes the twelve videos sound like one series. S06 (`S06/cues.json`) is the reference:
when in doubt, do what it does.

## Who is listening

A room of Civil Air Patrol cadets and senior members, 12 to 99 years old. Write for a sharp 12 to 14
year old who has never built a rocket. The adults in the room are fine with that; a 13 year old is not
fine with being talked down to. So: never "kids", "boys and girls", "guys" or "you might not know";
no exclamation marks; no jokes that need adult context; no hype words (awesome, super, epic, cool).
Assume they are smart and new. Explain, do not simplify away.

## How it sounds

- **Second person, present tense.** "You will fly it on a G." "Air pushes at the CP."
- **Short sentences, one idea each.** Average under fifteen words. A long thought becomes two sentences.
- **Every technical term gets a plain-words definition the moment it first appears**, in the same
  breath: "A Newton is a push." "That point is the center of gravity, CG." Never define by another
  term the listener does not have yet.
- **Anchor every abstraction to the room.** The two rockets on the table are the running example:
  "the Alpha III you built this morning", "the BR-1 you are building right now", the G74 most of them
  will fly, the H that some of them will certify on. Say something like that at least twice per segment.
- **Numbers in words when spoken, digits on the slide.** `say`: "seventy-four Newtons". Slide:
  "74 N". Round when speaking ("about six hundred and forty metres"); be exact on the slide.
- **Both systems, imperial first.** Motors are labelled in grams and millimeters and OpenRocket can show
  either, so every number appears in both: on slides "27 1/2 in (70 cm)", "7.5 oz (212 g)", "694 ft
  (211 m)"; spoken as "twenty-seven and a half inches, seventy centimeters" the first time a number
  comes up in a cue, imperial alone when it is repeated in the same breath. Inches in fractions to the
  nearest eighth; metric as whole centimeters or millimeters, never decimal meters ("63 cm", not
  "0.63 m"). Mass in pounds and ounces with grams. Altitude and distance in feet with meters. Flight speed
  in mph with m/s; speed off the rail in ft/s with m/s. Motor diameters stay 29 mm. Force in Newtons.
  One exception: Segment 11 builds parts in OpenRocket, and the program builds in metric, so that segment's
  dimensions and masses read metric first ("203 mm (8 in)", "240 g (8.5 oz)") and it says why.
- **Other segments are named in words in narration** ("that is Segment twelve") and in digits on
  slides ("see Segment 12"). `normalize.py` enforces this and the spellings below.
- **Calm about safety.** No scare stories, no softening. State the rule and the reason. "Do what your
  RSO says."
- **Narrator says "you" and "the program".** Never "we" or "I" for the narrator. "The program flies a
  six second delay." "I" is fine inside a pause-card question ("I am about to slide a motor in").
- **"Let's" at most once per segment. No stacked rhetorical questions.** One question, then answer it.
- **Lists are lists.** An answer card is a short verdict in `text` and the reasons as `lines` bullets. A note or caption that holds parallel items separates them with "  ·  ", never a run of short sentences.
- **No em dashes or semicolons in narration.** Use a period. On slides use a colon or "  ·  ".

## Shape of a segment

Eight to eleven cues, in this order:

1. `title`. `say` opens exactly like S06: "Segment six. How a rocket motor is measured. By the end of
   this you will be able to ..." then the objective from the segment file, in one sentence.
2. Four to six teaching beats, one cue each, following the segment file's script outline in order.
   Each beat is one idea, 40 to 100 spoken words. Its slide carries the anchor (the number, the
   picture, the three-word rule), not a transcript of the narration.
3. Exactly one `pause` cue, using the question from the segment file's "Pause point" word for word.
4. An `answer` cue right after it. Its `say` starts with the answer in one word or phrase, then the
   reason, then usually stretches the idea one step further (S06: "Now stretch that...").
5. Optionally a bridge beat ("One last thing...") that hands off to the next segment by number.
6. `close`. `say` starts "The one thing to remember." and restates the single takeaway in one
   sentence, matching the close slide's text.

Length: 480 to 680 spoken words in total. S06 is 545 words and runs 3 minutes 23 seconds. Under 480
is thin; over 680 will run past the cure wait (saying every number in both unit systems costs about
ten percent). No single cue over 120 words.

## Slides

- Headings are three to six words. Bullet lines are eight words or fewer, three lines at most.
- A slide never repeats the narration verbatim. Slide text is the thing to remember; narration is
  the explanation.
- One `note` per slide at most, one sentence.
- The same palette and fonts for all twelve. Use the slide types in `render.py`; if a segment truly
  needs a new one, put it in `SNN/slides.py` (see README) and keep it to the same palette and helpers.
- No demos and no instructions to handle a rocket. Draw the idea (diagram, real data, a real photo from
  the build guide's `assets/img/`, or a screen recording for S11 and S12). Never fake a screenshot of
  software.

## Spellings and terms

Use these exact forms on slides and in `say`:

| Use | Not |
|---|---|
| high power rocketry, high power | high-power, HPR (on first use) |
| model rocket | low power rocket (except when quoting the range's "low power table") |
| motor | engine |
| center of gravity, CG · center of pressure, CP | centre |
| total impulse, Newton-seconds; on slides N·s | Ns, newton seconds |
| caliber, calibers | calibre |
| Alpha III · BR-1 · OpenRocket · RockSim | Alpha 3, BR1, Open Rocket |
| G74W-6, H128W-14, A8-3 (full code when the code matters; G74, H128 otherwise) | G-74 |
| NAR, Tripoli, RSO, LCO, FAA, L1 / Level 1 | T.R.A. |
| APCP, black powder | AP |
| meters, kilograms, grams, US spelling (spelled out in `say`; m, kg, g on slides) | metres, mm in `say` |

Pronunciation is handled centrally: `SAY_FIXES` in `render.py` already spells out CG, CP, RSO, NAR,
FAA, the program's motor codes, "Alpha III" and "BR-1" for the voice. For anything else a voice might
misread, add `"say_fixes": [["from", "to"]]` to the segment's `meta`; it applies to that segment only
and never touches the slide text or the reading script.

## Facts

Everything stated is checked against the segment file and, for numbers, against
`shared/br1-sim.json` (real OpenRocket results for the BR-1 on an H135W) and `shared/thrustcurves.json`
(certified data for the program's motors). Anything you could not verify goes in `SNN/CHECK.md` as a
one-line item for the program to confirm before the video is shown. Do not guess a number and present
it as fact; if a number is illustrative, the slide says "about" and CHECK.md says why.
