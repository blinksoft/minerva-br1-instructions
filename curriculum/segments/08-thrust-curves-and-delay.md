# S8 — Thrust curves and the delay

## Slot
First fin wait (step 22, first fin curing), 5 minutes. Fallback: 2:00 walkthrough block.

## Objective
The cadet can read a thrust curve, point to total impulse, peak thrust and burn time on it, and explain
what a wrong delay looks like on the field.

## Live on the day
Play the video. When the pause card comes up, pause it, take two or three answers from the room, then
press play. The video gives the answer. That is the whole job; no props, no setup.

## Script outline
1. **The picture behind the code.** Pull up thrustcurve.org and open a G74. Thrust on the vertical axis,
   time along the bottom. The area under the line is total impulse, the letter. The height of the line is
   thrust; the average across the burn is the number in the code.
2. **Shapes.** Some motors spike hard at the start and fade, good for kicking a heavy rocket off the rail.
   Some are flat, a steady push. Open an H128 next to the G74. Bigger area, longer burn. The shape is why
   two motors with the same letter fly the same rocket differently.
3. **Burnout, coast, apogee.** At burnout the motor stops but the rocket does not; it coasts upward,
   slowing. The top of the coast is apogee, the highest point and the slowest, and that is where you want
   the parachute out. Draw the arc on the board: burn, coast, apogee, descent.
4. **The delay decides the moment.** Too short and the chute opens while the rocket is still doing a
   hundred miles an hour: shredded chute, zippered tube. Too long and the rocket is nose-down and fast
   when the chute finally opens: same result, or worse. The right delay is the coast time, and that
   depends on how heavy and how draggy the rocket is.
   - **Pause card.** On screen: "Same rocket, same G motor, but a 12 second delay instead of 6. Where is the rocket pointing when the chute comes out?" Hold five seconds with a countdown, then a chime. On resume: Nose down and speeding up. It passed apogee six seconds ago. The chute opens into a fast, falling rocket: shredded chute or a zippered tube.
5. **How you find it.** OpenRocket simulates the flight and tells you the time from burnout to apogee.
   Pick the delay closest to that. For the BR-1 on a G74 the program uses a 6 second delay; in S12 you will
   see why.

## Demo, filmed
- Screen: thrustcurve.org, G74 and H128 pages side by side.
- Whiteboard arc of the flight with burnout, apogee and ejection marked.
- Optional prop: a chute that has been shredded by an early ejection, if the program has one.

## Pause point
After beat 4. The card reads: "Same rocket, same G motor, but a 12 second delay instead of 6. Where is the rocket pointing when the chute comes out?"

On resume the video answers: Nose down and speeding up. It passed apogee six seconds ago. The chute opens into a fast, falling rocket: shredded chute or a zippered tube.

## Shot list
- Screen capture: thrustcurve.org, zoom to the curve, cursor tracing the area, then the peak, then the
  burn time.
- Second curve alongside the first.
- Bench camera or drawn overlay: the flight arc.
- Screen capture insert: OpenRocket's motor selection dialog with its thrust curve preview.

- Pause card and answer card as full-screen title cards, see production.md.

## Check before filming
- The delay the program actually flies on the G74 and on the H, and the OpenRocket optimum delay for each.
- thrustcurve.org layout at recording time; describe what is on screen, not where the buttons were.

## Sources to replace
None. New material.
