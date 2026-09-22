# Minerva BR-1 instructions

Build guide and build-day curriculum for the Georgia Wing Civil Air Patrol High Power Rocketry
program's Minerva BR-1 rocket. Owner: Tim Perry. Audience 12 to 99, written for 12 to 14.

- `content/`, `assets/`, `build.py`, `index.html` — the assembly guide, published by GitHub Pages
  (`deploy.yml` runs on push to main).
- `files/BR-1.ork` — the program's OpenRocket design. Every stability or flight number in the
  guide and the videos comes from this file via `curriculum/video/shared/extract_ork.py`.
- `curriculum/` — twelve "While the epoxy cures" segments, one outline per segment in
  `segments/`, the run sheet, and `production.md` (which video ID is live).
- `curriculum/video/` — the video pipeline. Read its README before touching it.
- `videos/` — rendered MP4s, captions, thumbnails, `youtube.json` (live IDs). Committed.
- `recordings/` — raw OBS screen recordings, git-ignored. The cut clips in `S11/assets/` and
  `S12/assets/` are what the repo keeps; `shared/cut_clips.py` re-cuts them from `clips.json`.

## Working rules

**Commits and pushes are Tim's call.** Never commit or push unless he says so. A push to main that
touches `cues.json`, `assets/`, `render.py` or `publish.py` runs the publish workflow, which renders,
uploads changed videos to YouTube, deletes the superseded ones and commits the new IDs back. A push
is a publish.

**Narration costs money.** ElevenLabs audio is cached per cue in `SNN/narration/` by a hash of the
spoken text and voice. Only cues whose words change are re-bought. During a script review, edit
freely but do not run `render.py` until the review is done; `render.py SNN --slides` draws the
slides for free. Tell Tim which cues will re-buy before a render.

**Voice contract is `curriculum/video/STYLE.md`**, enforced by `lint.py` (run it on every segment
before a render; the workflow runs it too). The rules people have had to restate:
- The narration never instructs the room to handle a rocket during a cure wait. Describe, do not
  command. No demos, no props: the video carries the lesson.
- No swing test, ever, even as an aside. It has damaged too many rockets. Stability is checked in
  OpenRocket and by balancing on a finger against the sim's CG.
- Units: imperial first with metric in parentheses (inches to the nearest 1/8, lb and oz, cm or mm,
  never decimal metres). S11 alone is metric-first because OpenRocket parts are built in mm and g.
- The G74 and the H are a roughly even split of flyers. Say "some of you", never "most of you".
- The program flies only AeroTech DMS 29 mm motors: G74W and whichever H is on hand. No reloads.
- NAR is spoken as a word (rhymes with bar), set in `SAY_FIXES` in `render.py`.
- Lists are lists: answer cards are a short verdict plus bullets; a note or caption with parallel
  items uses "  ·  " separators, never a run of short sentences.
- Stability numbers come from the `design` block of `shared/br1-sim.json` (CP at zero angle of
  attack, Mach 0.3, what OpenRocket's design window shows), not the first sample of a flight.
  Rule of thumb taught: 1 to 3 calibers. When Tim drops a new `BR-1.ork` in the repo root, move it
  to `files/` and re-run `extract_ork.py`.

**Each segment has a `CHECK.md`** of facts to confirm. Tim answers in that file; fold the answers
into the cues and delete the resolved items. `review.py` regenerates `REVIEW.md`, the walk-through
sheet.

## YouTube

- `publish.py --status` shows what is live. Credentials: `.env` (gitignored) and
  `~/.config/ga-wing-youtube/`; the same values are repository secrets for the workflow.
- YouTube cannot replace a video's file. A changed render uploads a new video, then deletes the
  old one; links change. `youtube.json` and `production.md` hold the current IDs.
- Thumbnail uploads hit a separate rate limit ("too many thumbnails recently", HTTP 429) after
  about eight in a row. `publish.py` records which videos still need one and retries on every
  run, including the nightly run at 06:00 UTC. `publish.py --thumbnails` retries by hand.
- If a video sits at "processing will begin shortly" for more than fifteen minutes, set that
  segment's `outputSha` in `youtube.json` to any other string and run `publish.py SNN`; it
  re-uploads and deletes the stuck one.
- A first render on a new Google Cloud project allows about four full publishes a day.

## Environment notes

- Use the repo venv: `.venv/bin/python` (ffmpeg comes from `imageio-ffmpeg` inside it).
- This WSL host gets intermittent TLS handshake timeouts to ElevenLabs, thrustcurve.org and
  GitHub. The scripts retry; if something fails on the first try, run it again.
- Editing `render.py` while a render is running leaves segments fingerprinted against code they
  were not drawn with. Wait for the render to exit, then edit, then re-render.
