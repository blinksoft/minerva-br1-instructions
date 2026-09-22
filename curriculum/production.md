# Producing the videos

## Format

- 3 to 5 minutes. One idea per video. If a segment wants to be seven minutes, split it.
- Open with the "Ask the room" question. Close with the one sentence they should remember.
- Landscape, 1080p. Anything shown on screen must be readable on a phone at arm's length: big text,
  zoomed-in OpenRocket windows, no tiny toolbars.
- Captions on every video. YouTube auto-captions are a starting point; fix the rocketry terms by hand
  (Barrowman, Newton-seconds, APCP, caliber).
- Record each segment in one take. Trim the ends, add captions, done. No music, no title animation.
- The demo is in the video, always. The room only has five minutes, so anything that needs a prop built,
  a fan plugged in or a program opened is filmed, not performed live. Plan each shoot around getting the
  demo right on camera; the talking part is easy to redo.

## Two setups

**Bench camera** for props and demos (S1–S6, S9, the closing shot of S12).
- Phone on a tripod, looking down at the bench from about 45 degrees.
- A plain background: the same brown craft paper the build tables are covered in.
- A lapel mic or a second phone recording audio close to the speaker. Room audio from a tripod is the
  single most common reason instructional videos are unwatchable.
- Light from the side, not behind the speaker.

**Screen capture** for OpenRocket and thrustcurve.org (S7 partly, S8, S10–S12).
- OBS Studio (free) capturing one window, plus the same mic.
- Set OpenRocket's window to 1280×720 before recording so everything scales up cleanly.
- Increase the font size in OpenRocket preferences. Zoom the rocket view so the CP and CG markers fill the
  frame.
- Keep the mouse slow. Pause on every number you read aloud.

## Pause card and answer card

Every video has one pause point where the room is asked a question. It is built into the video so any
instructor delivers it the same way.

- **Pause card.** Full-screen title card, large text, the question exactly as written in the segment's
  "Pause point" section. Under it, smaller: "Pause here. Ask the room." A visible five-second countdown
  and a soft chime at the end, so an instructor who misses the cue still has time, and a class watching
  without an instructor still gets a beat to think.
- **Answer card.** Right after the countdown, a second card with the answer in one or two lines, then
  the video continues into the demo or the next beat that proves it.
- Keep both cards in the same style across all twelve videos: same font, same colours, same chime.
  Make them once as a template.
- Screen-capture segments: cut to the card, do not overlay it on the OpenRocket window.

## Slate

Start every recording with a card or a spoken line: segment number, title, date, and the guide version
(the commit hash or date from the footer). It makes re-recording one segment painless.

## Narration

Generated with ElevenLabs (see video/README.md). Two voices alternate so the series does not sound like
one long lecture: Josh ("Teacher for kids") on odd-numbered segments, Nichalia Schwartz ("Bright and
Friendly") on even-numbered ones. Say in each video description that the narration is synthesized.

## Hosting

- Channel: "GA Wing AeroSpace and STEM Education", https://www.youtube.com/@GAWingAEO (channel ID
  UC2rKU8yu51uJERekCOsdtYQ), phone-verified. Upload into an
  unlisted playlist named "BR-1 Build Day". Unlisted keeps them out of search but lets anyone with the
  guide link watch. Switch to public later if wanted.
- Publishing is automated: `curriculum/video/publish.py`, run nightly by GitHub Actions, uploads any
  changed render with its thumbnail and captions, adds it to the playlist, deletes the superseded video
  and fills in the table below. `videos/youtube.json` is the authoritative list of live video IDs.
- The MP4 masters are committed in `videos/` and served by GitHub Pages, so each one is also directly
  shareable at `https://blinksoft.github.io/minerva-br1-instructions/videos/S06.mp4` and survives any
  change to the YouTube channel.
- Record the YouTube ID and the master filename for each segment in the table below as they are made.

| # | Title | Voice | YouTube ID | Master file | Recorded |
|---|---|---|---|---|---|
| S1 | What is high power rocketry? | Josh | EMf62x6zXu0 | videos/S01.mp4 | published 2026-09-22 |
| S2 | NAR, Tripoli and certification | Nichalia | LDCboFxTcVI | videos/S02.mp4 | published 2026-09-22 |
| S3 | Center of gravity | Josh | K72AKyiQYYw | videos/S03.mp4 | published 2026-09-22 |
| S4 | Center of pressure | Nichalia | SxHvgvVJ-f4 | videos/S04.mp4 | published 2026-09-22 |
| S5 | Stability margin | Josh | EEmBGtfG09Q | videos/S05.mp4 | published 2026-09-22 |
| S6 | How a motor is measured | Nichalia | 9QVB42KrN1E | videos/S06.mp4 | published 2026-09-22 |
| S7 | Reading the motor code | Josh | PqqFyUP5h38 | videos/S07.mp4 | published 2026-09-22 |
| S8 | Thrust curves and the delay | Nichalia | Mxy-jpmyiDw | videos/S08.mp4 | published 2026-09-22 |
| S9 | Motor sizes, types and safety | Josh | y2lvHdUAGZU | videos/S09.mp4 | published 2026-09-22 |
| S10 | Why simulate, and what tools exist | Nichalia | g4YKIFKWCks | videos/S10.mp4 | published 2026-09-22 |
| S11 | Building a rocket from scratch in OpenRocket | Josh | yvPDSQfPAOY | videos/S11.mp4 | published 2026-09-22 |
| S12 | Stability with and without a motor | Nichalia | xcXoR-tNCdA | videos/S12.mp4 | published 2026-09-22 |

## How the guide page will show them (not built yet)

When videos exist, the guide gets a `lesson` card type in content/steps.json, rendered by build.py
between the build steps it belongs with. Planned shape:

```json
{
  "lesson": "S4",
  "title": "Center of pressure",
  "slot": "While the motor mount cures",
  "summary": "One paragraph from the segment's Objective.",
  "youtube": "VIDEO_ID",
  "mp4": "https://…/S04-center-of-pressure.mp4",
  "minutes": 4
}
```

The card shows the title, the summary, an embedded player (YouTube ID first, MP4 as fallback) and a
"Watch later" checkbox that uses the same progress storage as the build steps. The segment files' fixed
headings map onto that card one to one, so nothing needs rewriting when the time comes.
