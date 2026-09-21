# Generating segment videos

Slides, narration, pause card and captions are built from one JSON file per segment. Nothing is filmed.
Where a segment calls for a real shot (see each segment's "Demo, filmed" list), the generated video
stands in until that shot exists.

```
curriculum/video/
  render.py             the renderer
  fonts/                Inter (OFL licence), used on every slide
  S06/cues.json         one segment: slide list with narration text        <- the only file you edit
  S06/assets/           photos and data the slides use (apple photo, thrust curve data)
  S06/narration/        synthesized narration, one MP3 per cue, named by content hash   (committed)
  S06/slides/           every rendered slide as a PNG, for reuse elsewhere              (committed)
  S06/script.md         generated: the narration as a numbered reading script
  S06/voice/NN.wav      optional: a real person's recording of cue NN, overrides narration/
  out/work/             scratch (ignored)
videos/
  S06.mp4, S06.srt      the finished video and captions, served by GitHub Pages          (committed)
  S06.sha               fingerprint of the inputs that produced it
  S06.youtube.md        upload kit: title, description, tags; S06-thumb.jpg the thumbnail
  youtube.json          which video ID is live for each segment                            (committed)
```

## The rule: generate once, commit the result

Everything that costs money or time to produce is committed, and the renderer reuses it:

- **Narration** is bought from ElevenLabs once per cue wording. The file name carries a hash of the
  spoken text and the voice. Edit one cue's words and only that cue is re-synthesized; the old file is
  removed. Nothing is re-bought on a fresh checkout or another machine.
- **Slides** are drawn by code from the cue file, fonts, photos and data, all in the repo. No AI is
  involved, so they cost nothing to redraw, and each render also saves them as PNGs.
- **Assets** such as photos or downloaded data live in the segment's `assets/` folder. If an image is
  ever AI-generated, it is saved there too and never regenerated.
- **The video** is only re-encoded when a segment's inputs change. `videos/SNN.sha` is a fingerprint of
  the cue file, assets, narration, recorded voice and the renderer; if it matches, the segment is
  skipped. `--force` overrides.

## One-time setup

Python 3 with Pillow and a bundled ffmpeg. Piper is only needed for the free fallback voice.

```bash
python3 -m venv .venv
.venv/bin/pip install -r curriculum/video/requirements.txt
.venv/bin/pip install piper-tts        # only for the free fallback voice
```

## Narration engine

Two engines. The renderer picks ElevenLabs when its key is present, otherwise Piper.

**ElevenLabs** (the program's subscription). Put the key in a `.env` file at the repo root, which is
gitignored:

```
ELEVEN_LABS_API_KEY=sk_...
ELEVEN_LABS_VOICE=josh                   # optional override: josh, nichalia, or any voice ID
```

The key only needs the `text_to_speech` permission. Narration is saved per cue in the segment's
`narration/` folder and committed, so a re-render only spends characters on cues whose text changed.
A full segment is about 3,000 characters the first time and nothing after that.
The program's two voices are Josh ("Teacher for kids") and Nichalia Schwartz ("Bright and Friendly"),
named in `VOICES` in render.py. Segments alternate: odd numbers are read by Josh, even numbers by
Nichalia. A segment can override with `"voice": "josh"` in its cues.json `meta`. For any other voice,
copy its ID from the ElevenLabs web library. To use a
clone of an instructor's voice, create it in ElevenLabs and use that voice's ID the same way.

**Piper** (free, local, the fallback):

```bash
mkdir -p ~/piper && cd ~/piper
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
export PIPER_VOICE=~/piper/en_US-lessac-medium.onnx
```

Set `TTS_ENGINE=piper` to force it even when the key is present.

Words the voices misread are fixed in `SAY_FIXES` in render.py, which is applied to the spoken text
only. "Alpha III" is spoken as "Alpha Three"; the slides and the reading script keep the real spelling.

## Render

```bash
.venv/bin/python curriculum/video/render.py S06          # one segment
.venv/bin/python curriculum/video/render.py all          # every segment; unchanged ones are skipped
.venv/bin/python curriculum/video/render.py S06 --force  # rebuild regardless
```

Produces `videos/S06.mp4` (1080p, H.264, AAC) and `videos/S06.srt` captions for YouTube, refreshes
`S06/script.md`, and saves the slides to `S06/slides/`. Each cue becomes one slide whose length follows
its narration audio. Commit `videos/`, `narration/` and `slides/` along with the cue file.

## Replacing the synthetic voice with a recorded one

1. Open `S06/script.md`. It lists every cue with the exact words.
2. Record one file per cue, named `S06/voice/01.wav`, `02.wav`, and so on. Phone voice memo is fine;
   convert to wav, or change the extension check in render.py to accept m4a. Leave a short silence at
   each end. Read it in your own words if you like; the slide text is the anchor, not the script.
3. Run render.py again. Any cue with a recorded file uses it instead of `narration/`; the rest keep the
   synthetic voice, so you can record in several sittings.
4. The captions file is generated from the script text. If you departed from the script, edit the
   `say` text in cues.json to match what you said before the final render.

## The pause card

A cue of type `pause` renders as a five-second countdown with a chime on the last second. The room's
instructor pauses when it appears, takes answers, and presses play. The cue after it should be type
`answer`.

## Adding a segment

Copy `S06/cues.json` to `S07/cues.json`, change `meta` and the cue list, run the renderer. Slide types
available: `title`, `text`, `photo` (image from the segment folder, with optional badge and credit), `curves` (real thrust curves from a thrustcurve.org data file in the segment folder), `ladder`, `compare`, `pause`, `answer`, `close`. New
slide types are one function each in render.py; keep them to the same palette so the twelve videos
look like one series.

## Publishing to YouTube

`publish.py` uploads changed renders to the program channel (https://www.youtube.com/@GAWingAEO):

```bash
.venv/bin/python curriculum/video/publish.py --auth     # once: sign in as the channel owner
.venv/bin/python curriculum/video/publish.py S06        # or all
.venv/bin/python curriculum/video/publish.py --status
```

A segment is published when the rendered output, the MP4 plus captions, differs by content hash from
what is live in `videos/youtube.json`. Re-rendering follows the inputs; publishing follows the output, so
a renderer change that produces identical bytes uploads nothing. YouTube cannot replace a video's file,
so a changed output is a new upload: title, description and tags
from `videos/SNN.youtube.md`, thumbnail, captions, placed in the "BR-1 Build Day" playlist in segment
order, then the superseded video is deleted and the new ID is written to `videos/youtube.json` and the
table in `curriculum/production.md`. Anything that embeds a segment should read the ID from
`videos/youtube.json`.

Credentials: the OAuth Desktop client JSON as `GOOGLE_AUTH_JSON` and the token from `--auth` as
`YOUTUBE_TOKEN_JSON`, either inline or as file paths, in `.env` locally and as repository secrets in
GitHub Actions. Two Google limits apply: a new API project gets quota for about four full publishes a
day (the script stops cleanly and the nightly run continues), and until the project passes Google's
YouTube API compliance audit, uploaded videos are forced to private and must be flipped to Unlisted
in YouTube Studio; the script prints a note when that happens.

## CI/CD

`.github/workflows/publish.yml` runs nightly, on demand (Actions, "Render and publish segment videos",
Run workflow, optionally one segment and force), and on any push to main that touches a cue file,
segment assets, recorded voice or the two scripts. It renders what changed, publishes what changed,
commits `videos/`, narration, slides and the production table back to main, and triggers the Pages
deploy so the site serves the new files. Secrets needed: `ELEVEN_LABS_API_KEY`, `GOOGLE_AUTH_JSON`,
`YOUTUBE_TOKEN_JSON`.

The committed MP4 is the master copy, and because GitHub Pages serves the repo, each video is also
directly shareable at `https://blinksoft.github.io/minerva-br1-instructions/videos/SNN.mp4`.
