# While the epoxy cures — build-day curriculum

Short teaching segments, 3 to 5 minutes each, that fill the epoxy waits during the Minerva BR-1 build.
Each segment stands alone, is tied to a cure slot in the build, and is written as a script outline that
the program's own generated video follows instead of relying on YouTube links.

The build steps referred to here are the numbered steps in the assembly guide
(https://blinksoft.github.io/minerva-br1-instructions/). Each video is itself a numbered step in the
guide, placed at the cure wait it fills; the guide reads the live YouTube IDs from videos/youtube.json.

## Who this is for

12 to 99 year olds: CAP cadets and senior members, most with no rocketry background. Under-14s and anyone
not certifying fly the BR-1 on a G74-6 class motor. NAR Junior Level 1 (14 and up) and adult Level 1
candidates fly it on an H115 to H189 depending on what is available. Same airframe, all 29 mm motors.

## The day

| Time | Build activity | Wait | Segment |
|---|---|---|---|
| 8:30 | Alpha III low-power build | glue waits | S1 |
| 9:30 | Parts and tools, safety, rail buttons (steps 2–3) | superglue, about 1 min | – |
| 9:45 | Motor mount, steps 4–11 | 5 min after step 9, 5 min after step 11 | S2 (step 10), S3 (step 12) |
| 10:05 | Step 13, motor mount cure | 20–30 min | S4, S5 (steps 14–15) |
| 10:35 | Eyebolt, step 17 epoxy on the back of the rings | 5–10 min | S6 (step 18) |
| 10:50 | Kevlar, install steps 22–25, 15-minute epoxy | sets before lunch | S7 (step 27) if time allows |
| 11:30 or 12:00 | Lunch, hydro-dip nose cones; the install cures fully meanwhile | 30 min | – |
| after lunch | Step 26, aft joint | 5 min | S7 (step 27) if not done, else buffer |
| +10 min | Fins, step 29, one at a time | 3 × 5 min | S8, S9, S10 (steps 30–32) |
| +40 min | Fillets, step 33, three rounds | 3 × 5 min | S11, S12 (steps 34–35); round three is a spare |
| +75 min | Recovery harness, decorate | none | open Q&A |
| about 2:00 | OpenRocket walkthrough, homework, slack | | live version of S10–S12 |
| 3:30 | Done | | |

The morning goal is the motor mount built and installed, then lunch. Lunch lands at 11:30 or 12:00
depending on how fast the class moves, so the afternoon rows are given as offsets from the end of lunch.
Times are targets, not a schedule. The last hour or so is deliberately loose because a room of
12-year-olds runs slow, and anything that slips lands there. Every segment lists a
fallback slot so an instructor can shuffle the order without losing anything.

Teaching time adds up to about 50 minutes. The afternoon has exactly seven 5-minute waits (aft joint,
three fins, three fillet rounds) and segments S7 to S12 need six, so the third fillet round is a spare,
and so is the aft-joint wait if S7 happens before lunch.

## Segments

| # | File | Topic | Slot | Guide step |
|---|---|---|---|---|
| S1 | segments/01-what-is-high-power.md | What is high power rocketry? | Alpha III glue wait | 1 |
| S2 | segments/02-nar-tripoli-certification.md | NAR, Tripoli and certification | Step 9 wait | 10 |
| S3 | segments/03-center-of-gravity.md | Center of gravity | Step 11 wait | 12 |
| S4 | segments/04-center-of-pressure.md | Center of pressure | Step 13 cure | 14 |
| S5 | segments/05-stability-margin.md | Stability margin | Step 13 cure | 15 |
| S6 | segments/06-how-a-motor-is-measured.md | How a motor is measured | Step 17 wait | 18 |
| S7 | segments/07-reading-the-motor-code.md | Reading the motor code | Before lunch while the install sets, or the step 26 wait | 27 |
| S8 | segments/08-thrust-curves-and-delay.md | Thrust curves and the delay | First fin wait (step 29) | 30 |
| S9 | segments/09-motor-sizes-types-safety.md | Motor sizes, types and safety | Second fin wait (step 29) | 31 |
| S10 | segments/10-why-simulate.md | Why simulate, and what tools exist | Third fin wait (step 29) | 32 |
| S11 | segments/11-openrocket-from-scratch.md | Building a rocket from scratch in OpenRocket | Fillet round one (step 33) | 34 |
| S12 | segments/12-stability-with-and-without-motor.md | Stability with and without a motor | Fillet round two (step 33) | 35 |

The four topic areas map to segments like this: high power and NAR (S1, S2), stability (S3–S5), motors
(S6–S9), OpenRocket (S10–S12).

## The rule: the video carries the lesson

A cure wait is five minutes and the video is three to five. There is no time for props, demos or opening
OpenRocket in the room, and nothing is done to a rocket during the wait. In the room a segment is: press
play, pause when the card says to, take a few answers, press play. Even the question is in the video, so
every instructor delivers the same material the same way. run-sheet.md is the one-page version of the day
for whoever is leading.

## How each segment file is laid out

Every file has the same headings, in this order (the guide's video steps carry the objective in one
line and link to the video):

1. **Slot** — where it goes in the day, plus a fallback.
2. **Objective** — one sentence: what the cadet can do afterward.
3. **Live on the day** — what the instructor does in the room. Always short.
4. **Script outline** — four to six beats of about a minute each, for the video. Not a word-for-word
   script; the person recording should talk it in their own voice.
5. **Pause point** — the one question built into the video as a pause card, where it sits in the
   script, and the answer the video gives on resume. The instructor pauses, takes answers, presses play.
6. **Shot list** — one line: the video is slides, a pause card and an answer card (S11 and S12 add
   screen recordings of OpenRocket).
7. **Check before showing** — facts to verify against the current NAR / Tripoli / FAA rules before the
   day, because these change. Nothing in a segment should be shown until it is checked.
8. **Sources to replace** — the YouTube clip this segment replaces, if any.

## Buffer material

If a cure runs long and every planned segment is used up:

- **Hydro-dip mass check.** Weigh a nose cone before and after dipping. Ask where that mass sits and what
  it does to CG (S3) and to the sim (S12).
- **Parachute sizing rule of thumb.** Aim for a descent of roughly 15 to 20 feet per second. Too slow and
  the rocket drifts off the field; too fast and fins break.
- **Launch-day checklist.** Motor retainer tight, igniter in last, rail buttons slide freely, shock cord
  packed so it cannot snag, chute dusted with talc, RSO check before you walk to the pad.

## For instructors

run-sheet.md is the printable one-page version of this: what to build, which video to play at each wait,
what to do at a pause card, and what to skip if the day runs late.

## Recording and generating

See production.md for the recording format, the pause and answer cards, hosting, and how the guide page
will embed the videos later. video/README.md covers the generated videos: slides, placeholder narration,
pause card and captions are built from one cue file per segment, and a recorded voice drops in afterward
without re-editing. All twelve segments are built this way; STYLE.md in that folder is the voice contract and REVIEW.md the walk-through sheet.
