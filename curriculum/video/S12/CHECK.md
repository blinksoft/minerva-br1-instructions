# S12 — check before the video is shown

- The exact G and H motors the program flies this season are present in OpenRocket's motor database (BR-1.ork holds G74W-6, H135W-8 and H115DM-8; the video names G74W-6 and H135W-8).
- BR-1.ork mass overrides updated from a real weighed rocket, so the on-screen numbers are believable (video quotes 2 lb 5 oz loaded with the G, 2 lb 9 oz with the H, CG 26 in and 27 1/2 in, margins 2.47 and 1.99 calibers, apogees 705 ft and 2,150 ft).
- The program's stability margin target for an L1 flight, if it differs from the general 1 to 2 calibers (the video says the H flight "deserves a second look ... sometimes a little nose weight" without naming a target).
- CP is 33 3/4 in on every rocket slide: the design-window value at zero angle of attack and Mach 0.3, from the file's `design` block. The in-flight CP wanders 31 1/2 to 33 1/2 in with angle of attack and is not what the video quotes.
- Empty-rocket CG "24 3/4 in" (24 3/4 in) and "about 2.6 calibers" are estimates: each configuration's motor removed from its on-pad CG, not a stored OpenRocket number; confirm against the design window with no configuration selected.
- The "Margin through the burn" plot is the margin against the design CP (`marginCal`, 2.47 on the pad to 2.69 at burnout). OpenRocket's own stability plot uses the in-flight CP and will look lower early on (about 1.7 leaving the rail on the G); the shape and the burnout value are the same.
- G run four numbers and delay: apogee 705 ft at 6.8 s, top speed 153 mph, 54 ft/s off the 72 in rail, ejection at 7.2 s, optimum delay 5.6 s, all from the stored run 3 events and summary; narration rounds to "about two hundred and ten", "sixty-nine" and "twelve".
- H run four numbers and delay: 2,150 ft at 10.4 s, 339 mph, 68 ft/s off the 72 in rail at 3 degrees, ejection at 10.1 s, optimum delay 8.5 s, from stored run 1; they appear in the run slide's caption, not as a second chart, to stay within eleven cues.
- Cue 9 (wind and rail angle) is the recorded ground-track sequence on the real file's H run 1 (72 in rail at 3°,
  4 mph wind): lands about 440 ft out on the plot (the stored run says 400 ft; narration says "about four hundred");
  then the same run edited to 20 mph wind, landing about 2,500 ft out ("nearly half a mile"); then the rail at 15°
  into that wind, about 1,400 ft; then 30°, near the pad. Those three edited runs exist only in the recording,
  read off the plot axes, not in BR-1.ork. "The most the safety code allows" is the NAR 20 mph wind limit and
  30° is the NAR maximum launch angle.
- "Spent casing balances at 25 1/4 in" uses the sim's burnout CG with the G (25 1/4 in, motor mass 1.7 oz); a real spent casing after ejection is a little lighter, so expect the balance point a touch further forward.
- The H slide's note "Burnout: 2.3 calibers" is the H's `marginCal` at 2.1 s (2.9 oz of propellant gone, CG 26 1/2 in); narration does not read it aloud.
- Departure: beat 6, the bench camera shot of the rocket balanced on a finger, is not filmed; a rocket slide with the live-motor and spent-casing CG markers stands in.
- Cues 3, 7, 8, 9 and 10 are screen recordings from 2026-09-21 (see S11/RECORDING.md). Cue 3 opens on the
  from-scratch example's New Configuration dialog (its readout says 2.85 cal) and cuts to the real file's G74W-6
  readout (2.51 cal, CG 25.995 in); cue 7 likewise shows the H135 being picked with an 8 s delay on the example,
  then the real file's H135W-8 readout (2.03 cal, CG 27.486 in). Cue 8 is the real file's sim table, cropped:
  G74W-6 54.2 ft/s, 705 ft, 5.68 s, 226 ft/s, 6.82 s; H135W-8 67.8 ft/s, 2150 ft, 8.57 s, 498 ft/s, 10.4 s.
- Cue 2 (empty rocket) and cue 6 (margin plot) stay drawn: the recording never shows the real file with
  [No motors] selected or a stability-against-time plot. A 15-second pickup of either can replace them.
- Cue 9's narration changed for the footage and is re-narrated at the next render; every other cue is cached.
