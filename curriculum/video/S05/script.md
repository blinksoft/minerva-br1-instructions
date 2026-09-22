# S05 — Stability margin and the swing test: narration script

Record one file per numbered cue, as `voice/NN.wav` (any sample rate, mono is fine).
Leave a beat of silence at the start and end of each. Re-run render.py and the slides
re-time themselves to your voice.

**01** `voice/01.wav`

Segment five. Stability margin and the swing test. By the end of this you will be able to state the stability rule, say what happens when it is broken in either direction, and run a swing test.

**02** `voice/02.wav`

Put the two dots together. Segment three gave you the center of gravity, CG, the balance point. Segment four gave you the center of pressure, CP, the point where the air pushes. A rocket flies straight when the CG is in front of the CP. The air pushes at the CP. The rocket pivots around the CG. A push behind the pivot swings the nose back into the wind. That is a weathervane. On the BR-1 with the G74 loaded, the CG is here, and the CP is behind it, near the fins.

**03** `voice/03.wav`

Now, how far in front. Measure from the CG to the CP and divide by the body tube diameter. That is the stability margin, in calibers. One caliber is one body diameter. On the BR-1 with the G74 loaded, OpenRocket puts the CG twenty-six inches, sixty-six centimeters back from the nose and the CP thirty-three and three quarters. The gap is seven and three quarter inches, twenty centimeters, the tube is three and an eighth across, eight centimeters, and that divides to about two and a half calibers. The rule: one to three calibers is the target. Under one is risky. Over three is a different problem.

**04 — pause card, no narration.** The card reads: _This rocket has its CG one diameter ahead of its CP. I load a heavier motor. More stable or less?_

**05** `voice/05.wav`

Less. The motor is mass at the back. Add more of it and the CG slides aft, toward the CP, so the margin shrinks. That is why the loaded rocket is what you check. With the G74, about three ounces, eighty-seven grams, the BR-1 sits at two and a half calibers. Load the H135 instead, seven and a half ounces, two hundred and twelve grams, and the margin drops to two. Same airframe, more mass at the back, smaller margin. What the burn itself does to the margin is Segment twelve.

**06** `voice/06.wav`

Too little margin, and the rocket tumbles. With the CG behind the CP, the air's push is in front of the pivot. Any wobble grows instead of shrinking. The rocket cartwheels off the pad. Throw a paper airplane with no paperclip on its nose. It flips, stalls and tumbles, because its balance point is too far back. Under one caliber, a rocket is heading the same way.

**07** `voice/07.wav`

Too much margin, and the rocket weathercocks. A very stable rocket turns hard into any crosswind and flies sideways instead of up. Lower apogee, and a long walk to get it back. Same paper airplane, two paperclips on the nose, thrown in front of a box fan. It turns into the wind and dives. Not dangerous the way tumbling is, but it costs you altitude.

**08** `voice/08.wav`

The swing test needs no computer. Load the motor. Find the balance point and tie a string there, at the CG. Go outside and swing it in a circle overhead. If the nose leads, steady, all the way round, the rocket is stable. If it flies sideways or backwards, do not launch it. Do this with the finished BR-1 before its first flight. In Segment twelve you will see OpenRocket work out the same number.

**09** `voice/09.wav`

The one thing to remember. CG ahead of CP by one to three calibers, with the motor loaded. Check it before you fly.
