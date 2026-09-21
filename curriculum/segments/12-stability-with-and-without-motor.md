# S12 — Stability with and without a motor

## Slot
Fillet round three (step 23), 5 minutes, with the 2:00 walkthrough block for the rest. Leads straight into
homework step 28.

## Objective
The cadet can add a motor to the OpenRocket model, see what it does to CG and stability, run a
simulation, and read apogee, rail-exit speed and the optimum delay.

## Live on the day
Play the video. When the pause card comes up, pause it, take two or three answers from the room, then
press play. The video gives the answer. That is the whole job; no props, no setup.

## Script outline
1. **Empty rocket first.** BR-1.ork open, no motor configuration selected. Read the stability margin
   aloud. Note where the CG dot is.
2. **Add the G74-6.** Motors and configuration, new configuration, pick the G74 with a 6 second delay.
   The CG dot slides aft, because a motor is a lump of mass at the very back. The stability number drops.
   This is the rocket on the pad, and it is the least stable it will ever be. As propellant burns off, CG
   moves forward and it gets more stable.
   - **Pause card.** On screen: "On the pad with the motor loaded, is this rocket more stable or less stable than it will be at burnout? Why?" Hold five seconds with a countdown, then a chime. On resume: Less. Propellant is mass at the very back. As it burns off the CG moves forward, away from the CP, and the margin grows through the burn.
3. **Add an H.** New configuration with an H128 or whatever the program flies. Heavier motor, CG further
   aft, stability lower still. This is why an L1 flight on the same airframe deserves a second look at the
   numbers, and sometimes a little nose weight.
4. **Run it.** Simulations, new, pick the G configuration, run. Read four numbers: apogee, maximum
   speed, speed leaving the rail, and time to apogee. Compare time to apogee against the 6 second delay.
   Then run the H and read the same four.
5. **Wind and angle.** Change the launch rod angle and the wind speed and run again. Watch the landing
   distance. This is the homework in step 28: play with these until you know how far you might have to
   walk.
6. **Close the loop.** Bench camera: the finished BR-1 with a spent G casing loaded, balanced on a
   finger. Compare the balance point to the CG the sim shows. If they match, the model is honest. Go fly.

## Demo, filmed
- Screen: BR-1.ork, motor database populated with the G and H the program uses.
- A finished BR-1 and a spent G casing for the closing shot.

## Pause point
After beat 2. The card reads: "On the pad with the motor loaded, is this rocket more stable or less stable than it will be at burnout? Why?"

On resume the video answers: Less. Propellant is mass at the very back. As it burns off the CG moves forward, away from the CP, and the margin grows through the burn.

## Shot list
- Screen capture: stability readout before and after each motor, held long enough to read.
- Simulation results table zoomed, cursor on each of the four numbers as they are read.
- Rod angle and wind change, rerun, landing distance.
- Bench camera closing shot: rocket balanced on a finger next to the screen showing the CG.

- Pause card and answer card as full-screen title cards, see production.md.

## Check before filming
- The exact G and H motors the program flies this season, present in OpenRocket's motor database.
- BR-1.ork mass overrides updated from a real weighed rocket, so the on-camera numbers are believable.
- The program's stability margin target for an L1 flight, if it differs from the general 1 to 2 calibers.

## Sources to replace
"Interpreting OpenRocket simulation results" (youtu.be/543Gnd63saM) and "Running a simulation in
OpenRocket" (youtu.be/H9S6yn9iwqc), both linked from homework step 28.
