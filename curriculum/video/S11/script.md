# S11 — Building a rocket from scratch in OpenRocket: narration script

Record one file per numbered cue, as `voice/NN.wav` (any sample rate, mono is fine).
Leave a beat of silence at the start and end of each. Re-run render.py and the slides
re-time themselves to your voice.

**01** `voice/01.wav`

Segment eleven. Building a rocket from scratch in OpenRocket. By the end of this you will be able to start a new OpenRocket design, add the parts of a simple rocket in the right order, then open the program's BR-1 file and understand what you are looking at.

**02** `voice/02.wav`

Start a new design and name it. It is empty, and it is a tree. At the top is a stage. Every part hangs off the stage, or off another part. Fins hang off a tube. Rings sit inside a tube. One rule before the first part. Engineers build in metric, and so does OpenRocket, so every number you type in this segment is millimeters and grams. The inches are there so you can picture it. The order is nose to tail: nose cone, body tube, then everything that lives inside the tube.

**03** `voice/03.wav`

Add a nose cone: for the BR-1, an ellipsoid two hundred and three millimeters long, eight inches, with a shoulder that slides into the tube. Add a body tube. Set the diameter and length: eighty millimeters across, nine hundred and forty long. Three and an eighth inches by thirty-seven. The moment there is a shape for air to push on, OpenRocket puts a red dot on it, the CP from Segment four. For now it sits near the nose, because the nose is the only thing pushing air aside.

**04** `voice/04.wav`

Now the inside. Select the body tube, so the next part hangs off it. Add an inner tube sized for the motor, and mark it as a motor mount. That is the tube you built this morning. Add two centering rings to hold it, one near the aft end and one six inches up, then a parachute and a shock cord. The blue dot, the CG, moves as each part goes in, toward whatever you added.

**05** `voice/05.wav`

Add a fin set to the body tube: three trapezoidal fins. Ninety millimeters along the root, three and a half inches. Sixty at the tip, ninety tall, with a fifteen millimeter sweep. Those are the BR-1's real fins, the ones you are filleting right now. Accept the dialog, and the red dot jumps toward the tail. In the program's file it lands at thirty-three and three quarter inches, eighty-six centimeters from the nose tip. Last, add the rail buttons. They add drag and mass, so they belong in the file.

**06 — pause card, no narration.** The card reads: _I added the fins and the red dot jumped toward the tail. Why the red one and not the blue one?_

**07** `voice/07.wav`

Area. Fins are a lot of area and very little mass. Area moves the CP, the red dot, because air pushes on area. Mass moves the CG, the blue dot, and three thin plywood fins barely move it. Now stretch that. Every part does one of two jobs. It gives the air something to push on, or it adds mass. Fins are almost all the first. A motor is almost all the second.

**08** `voice/08.wav`

Now the step most people skip. OpenRocket works out each part's mass from its material and size. That is a guess. So put the real part on a scale, and override its mass with what the scale says. The program's file does exactly this. The nose cone is set to two hundred and forty grams, eight and a half ounces. The body tube to three hundred and fifty-four, twelve and a half ounces. Those came from a scale, not a formula. Do this and the blue dot stops lying.

**09** `voice/09.wav`

Now open the program's file, BR-1.ork, next to yours. Same tree, same order, every number tuned to the kit on your table. With the G74 most of you fly loaded, the CG sits at twenty-six inches, sixty-six centimeters and the CP at thirty-three and three quarters. That gap is two and a half calibers, the stability margin from Segment five. Your from-scratch build teaches you what the file means. The program's file is what you fly. What the two dots do when the motor comes out is the next segment.

**10** `voice/10.wav`

The one thing to remember. In OpenRocket a rocket is a tree of parts. Area moves the CP, mass moves the CG, and a scale beats a guess.
