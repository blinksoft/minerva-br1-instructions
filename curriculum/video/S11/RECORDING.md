# Screen recording for S11 and S12

One sitting covers both segments: build the BR-1 from a blank OpenRocket, then add motors and run
simulations. Record it all in one take, in order. Nothing has to be clean: the synthetic narration
carries the words, so each cue only needs a few seconds of the right thing on screen, and the lead
cuts each clip to fit its narration. If a step goes wrong, redo the step and keep rolling.

## Setup (five minutes, once)

- OBS Studio, capturing the OpenRocket window, 1920×1080, 30 fps. No microphone needed; if you talk
  while you work, that audio is a useful reference for the edit but will not be used.
- OpenRocket window maximized. Preferences → increase the UI font size if the version offers it, so
  dialogs read on a phone. Zoom the rocket view so the whole rocket fills the width.
- Show CG/CP ticked from the first component onward. Units: millimetres and grams (Preferences → Units),
  the way parts are built; the video reads both.
- Have `files/BR-1.ork` ready to open at the end. Save your from-scratch build under a new name.
- Move the mouse slowly. After every dialog closes, take your hands off for two seconds: those are
  the cut points.

## S11 shot list, in the order the video plays

Type everything in millimetres and grams (Preferences → Units → metric). The video says so: engineers
build in metric, and so does OpenRocket.

| Cue | Show on screen | Screen time needed |
|---|---|---|
| 2 The rocket is a tree | File, New. Name it. The empty tree with one stage. Say "engineers build in metric" if you like; the narration does. | 25 s |
| 3 Nose to tail | Add a nose cone: ellipsoid, length 203 mm, base diameter 80.3 mm, and its shoulder: length 75 mm, wall 2 mm, diameter to fit inside the tube (76.2 mm with the 2.03 mm wall; the file still has 78.7 mm from the old tube, so check it). Override mass 240 g. Add a body tube: length 940 mm, outer diameter 80.3 mm (measured; the maker's sheet says 82.8), wall 2.03 mm. Override mass 354 g. Let the red CP dot appear. | 30 s |
| 4 Inside the tube | Select the body tube. Add an inner tube: outer diameter 30.9 mm, inner 29.2 mm, length 190 mm, tick "motor mount", override mass 30 g. Add a mass component inside it at the aft end, name it Motor Retainer, 20 g. Add two centering rings, 6.35 mm (1/4 in) thick, outer and inner radius on automatic so they fit the tube and the mount: one 5 mm from the aft end of the body tube, one 152 mm (6 in) from the aft end. Leave their mass alone. Add a parachute, 36 in / 914 mm, and a shock cord. Add mass components Shock Cord Hardware 50 g and Swivel and Ring 20 g. Watch the blue CG dot. | 25 s |
| 5 Fins | Add a trapezoidal fin set: 3 fins, root 90 mm, tip 60 mm, height 90 mm, sweep 15 mm, thickness 3 mm. Accept and let the red dot jump aft. Add two rail buttons, 2.9 g each. | 37 s |
| 7 Answer | Nothing new: a slow pan of the tree and the two dots is enough. | 28 s |
| 8 Make the masses honest | Open the nose cone's Override tab again and show the 240 g, then the body tube's 354 g, slowly: these are the two on camera. Then the final tree. Readout should be about 962 g with no motor. | 34 s |
| 9 Open the real one | File, Open, `BR-1.ork`, side by side or switching windows. Flight configuration G74W-6 so the readout shows 2.2 cal. | 34 s |

Rings, fins, parachute and cords keep OpenRocket's own mass from material and size; that is what the
video says. If the readout does not land near 962 g and 2.2 cal, say so on the recording and carry on.

## S12 shot list, straight after

| Cue | Show on screen | Screen time needed |
|---|---|---|
| 2 Empty rocket first | BR-1.ork, flight configuration set to none. Readout about 2.6 cal, CG 24 3/4 in. | 17 s |
| 3 Add the G74 | Motors & Configuration tab, new configuration, pick the G74W with the 6 s delay. Back to the design tab: 2.2 cal, CG 26 in. | 22 s |
| 5 Answer | Hold on the design view with the G74 loaded. | 29 s |
| 6 Margin through the burn | Optional: Flight simulations, plot Stability margin against time for the G run. The video has its own chart if you skip this. | 17 s |
| 7 Add an H | New configuration, H135W, 8 s delay. Design tab: 1.8 cal, CG 27 1/2 in. | 28 s |
| 8 Run it: four numbers | Flight simulations tab. New simulation on the G74W-6, launch conditions: 72 in rail, straight up, 4 mph wind, the field site. Run. Hover the results row: apogee, max velocity, velocity off the rail, time to apogee, optimum delay. Then the same for the H135W-8 with the rail at 3°. | 47 s |
| 9 Wind and rail angle | Edit the H simulation: rail angle 0° then 3°, wind 4 mph. Run. Show the landing distance (plot Lateral distance, or the results column). | 40 s |
| 10 Close the loop | Design view with the G74 loaded, CG readout 26 in. | 25 s |

The numbers in the tables are what the file gives today; if OpenRocket shows something slightly
different on the day, record what it shows and tell the lead, and the narration follows the screen.

## What was recorded (2026-09-21) and how it is used

Three OBS takes, now in `recordings/` (ignored by git; the cut clips are what the repo keeps):

| Take | Length | What it holds |
|---|---|---|
| `2026-09-21_23-32-57.mp4` | 30 min | the from-scratch build in metric, save as BR-1-Example, launch-site preferences, G74/H115/H128 configurations, sims, plots |
| `2026-09-21_23-38-30.mp4` | 3 min | the real `BR-1.ork` in inches: configurations, sim table, ground-track plots at 4 mph, 20 mph, 15° and 30° |
| `2026-09-21_23-54-31.mp4` | 1 min | adding the H135 to the example, wrong delay warning, delay set to 8, green check |

`SNN/assets/clips.json` lists the second ranges each clip is cut from; `python3 shared/cut_clips.py S11 S12`
re-cuts them. A `clip` cue in cues.json plays one, timed to its narration (see the README's slide table).

Used: S11 cues 2, 3, 4, 5, 8, 9 and S12 cues 3, 7, 8, 9, 10. Not used: the failed centering-ring attempts,
fin tabs, the shock-cord placement, the vertical-motion plot, the example's own sim table, the unit switch.

Still drawn, not recorded (optional 15-second pickups if wanted): S12 cue 2, the real `BR-1.ork` with
the flight configuration set to [No motors] and the readout held still; S12 cue 6, a Stability-against-time
plot for the G run. The narration for S12 cue 9 now follows the recorded ground tracks (3° rail in a 4 mph
wind, then 20 mph, then 15° and 30° into the wind) instead of the stored straight-up run.
