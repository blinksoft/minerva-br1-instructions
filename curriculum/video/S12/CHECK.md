# S11 check before showing

- OpenRocket version: menu names and dialog layouts change between releases, so the narration describes actions ("add a nose cone", "mark it as a motor mount", "override its mass") and never a menu path; confirm the actions read true in the version the room will use (the program's file is from OpenRocket 24.12).
- BR-1 dimensions on slides 3 to 5 come from shared/br1-sim.json, extracted from files/BR-1.ork: nose 8 in ellipsoid, body 37 in by 3 1/4 in, motor mount 29 mm by 7 1/2 in, three fins root 3 1/2, tip 2 3/8, height 3 1/2, sweep 5/8, 1/8 in thick; re-check if BR-1.ork changes.
- The segment file allows two 5-minute pieces; this is one 4.3-minute video covering beats 1 to 6, and the hands-on version happens in the live 2:00 OpenRocket walkthrough block.
- Slides 3 and 4 place the CP marker near the nose by reasoning only (an ellipsoid nose's CP sits about half way along it, and a plain tube adds none); the shared data has no fins-off CP, so no number is shown or spoken for it.
- Slides 4 and 5 place the CG marker at 24 3/4 in from the tip, the empty-rocket CG estimated in shared/br1-sim.json design.empty (a motor-removed estimate, not a value stored in the file); slide 5 shows it as "24 3/4 in" and no number is spoken for it.
- Slide 5 and its narration give the fins-added CP as 33 3/4 in "in the program's file"; that is the finished file's design-window CP (design.cpM 33 3/4 in, zero angle of attack, Mach 0.3), not the exact value at the instant fins are added in a from-scratch build.
- Slide 9's CG 26 in, CP 33 3/4 in and 2.2 calibers are the file's design-window values for the G74W-6 configuration (design.configurations: 26 in, 33 3/4 in, 2.47 cal, 2 lb 5 oz); the narration says the G74 is loaded.
- Slide 9's note and narration say the H reads 1.8 calibers: the H135W-8 configuration in the same design window (CG 27 1/2 in, CP 33 3/4 in, 1.99 cal, 2 lb 9 oz); the H115DM configuration has no stored stability figure, so it is not quoted.
- Nose cone 8.5 oz and body tube 12.5 oz are the values in shared/br1-sim.json massesKg; the narration presents them as mass overrides from a scale, so confirm they were measured, not calculated.
- "OpenRocket draws the CP as a red dot and the CG as a blue dot" is the default view; confirm for the version used. The slides keep the series colours (CG blue accent, CP orange).
- The `rocket` slide type always draws the rail-button stubs, and slide 4 shows the motor mount in orange before fins exist; the narration adds those parts in outline order, so the picture runs slightly ahead of the words on slides 3 and 4.
- Departures from the outline, all to stay menu-agnostic: "File, New" became "start a new design and name it"; "right-click a part" became "put the real part on a scale, and override its mass"; "click OK" became "accept the dialog".
- Nose cone shoulder in BR-1.ork is 78.7 mm diameter, 75 mm long, 2 mm wall; with the corrected 80.3 mm tube and 2.03 mm wall the tube's inside is 76.2 mm, so the shoulder in the file is oversize, and the recording shows 78.7 mm typed in. Fix it in BR-1.ork when convenient (it does not move the CP or CG enough to matter; nobody will read it off the clip).
- Cues 2, 3, 4, 5, 8 and 9 are screen recordings from 2026-09-21 (see RECORDING.md). Cues 2 to 8 show the
  from-scratch BR-1-Example, whose readout differs from the real file (empty 3.49 cal, 804 g, no rail buttons,
  shoulder still 78.7 mm); no narration quotes those example numbers. Cue 9 shows the real BR-1.ork in inches:
  G74W-6, 2.51 cal, CG 25.995 in, CP 33.913 in, which is what the narration says.
- Cue 5's narration ends "add the rail buttons"; the recording never adds them (the fin dialog is on screen).
- Cue 2's narration was changed for the footage: the parts table is gone, the empty tree and the metric
  preferences are on screen instead. Cue 2 is re-narrated at the next render; every other cue is cached.
- Clips are sped up or slowed to end with their narration ("stretch": cues 2 to 5, about 1.2 to 1.5 times)
  or hold their last frame ("hold": cues 8 and 9). If a stretched clip looks rushed, trim its ranges in
  assets/clips.json rather than slowing it.
