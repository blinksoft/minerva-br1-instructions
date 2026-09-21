# S11 — Building a rocket from scratch in OpenRocket

## Slot
Fillet rounds one and two (step 23), two 5 minute pieces. Cut at 5 minutes each; the 2:00 walkthrough
block picks up whatever is left. Fallback: 2:00 block entirely.

## Objective
The cadet can start a new OpenRocket design and add the parts of a simple rocket in the right order, then
open the program's BR-1 file and understand what they are looking at.

## Live on the day
Play the video. When the pause card comes up, pause it, take two or three answers from the room, then
press play. The video gives the answer. That is the whole job; no props, no setup.

## Script outline
1. **New design.** File, New. Name it. The rocket is a tree: a stage, and parts hanging off the stage.
   Parts hang off other parts: fins on a tube, rings inside a tube.
2. **The airframe, nose to tail.** Add a nose cone; set its shape and length. Add a body tube; set the
   diameter and length. These two give you the outside of the rocket. The CP dot appears the moment there
   is something for air to push on.
3. **Inside the tube.** Select the body tube and add an inner tube for the motor mount; set it to 29 mm
   and mark it as a motor mount. Add two centering rings to hold it. Add a parachute and a shock cord.
   Watch the CG dot move as each part goes in.
4. **Fins and rail buttons.** Add a trapezoidal fin set to the body tube: three fins, root and tip
   lengths, sweep, thickness. Watch the CP jump aft. Add rail buttons, because they add drag and mass too.
   - **Pause card.** On screen: "I added the fins and the red dot jumped toward the tail. Why the red one and not the blue one?" Hold five seconds with a countdown, then a chime. On resume: Fins are a lot of area and very little mass. Area moves the CP, the red dot. Mass moves the CG, the blue dot, and three thin plywood fins barely move it.
5. **Make the masses honest.** A part's mass comes from its material and dimensions, which is a guess.
   Right-click a part, override the mass with what a scale says, and the CG stops lying. This is the step
   most people skip, and the one that matters.
6. **Now open the real one.** Open BR-1.ork alongside. Same parts, same tree, tuned to the actual kit.
   The from-scratch build was to teach you what the file means; the program's file is what you fly with.

## Demo, filmed
- Screen only. A blank OpenRocket and BR-1.ork ready to open.
- Real fin, centering ring and nose cone on the bench for a one-shot cut to each as it is added.

## Pause point
After beat 4. The card reads: "I added the fins and the red dot jumped toward the tail. Why the red one and not the blue one?"

On resume the video answers: Fins are a lot of area and very little mass. Area moves the CP, the red dot. Mass moves the CG, the blue dot, and three thin plywood fins barely move it.

## Shot list
- Screen capture, split into two recordings at the natural break after beat 3.
- Cursor slow, every dialog left on screen long enough to read.
- Short bench-camera inserts of the real parts as each is added.

- Pause card and answer card as full-screen title cards, see production.md.

## Check before filming
- OpenRocket version; menu names and dialog layouts change between releases.
- Actual BR-1 dimensions from BR-1.ork so the from-scratch build matches the real rocket.

## Sources to replace
"Basics of OpenRocket" (youtu.be/z16_uUnMarE), the construction portion.
