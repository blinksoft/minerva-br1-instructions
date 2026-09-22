# S10 — Why simulate, and what tools exist

## Slot
Third fin wait (step 29), 5 minutes. Fallback: 2:00 walkthrough block.

## Objective
The cadet can say why we simulate before flying, name the two common tools, and recognise the CP and CG
markers and the stability number in OpenRocket.

## Live on the day
Play the video. When the pause card comes up, pause it, take two or three answers from the room, then
press play. The video gives the answer. That is the whole job; no props, no setup.

## Script outline
1. **A flight is a test you only get to run once.** A simulator lets you fly the rocket a hundred times on
   the screen before you fly it once for real. It tells you whether it is stable, how high it goes, how fast
   it leaves the rail, which delay to use, and roughly where it will land.
2. **Two tools.** OpenRocket is free, open source and runs on Windows, Mac and Linux. RockSim, from Apogee
   Components, is the paid alternative with a longer history and some extra features. Both answer the
   same questions. The program uses OpenRocket and gives you its BR-1 file.
3. **Open the BR-1.** Screen capture: open BR-1.ork. The side view shows the rocket as built. The blue dot
   is the CG, the red dot is the CP, and the number in the top corner is the stability margin in calibers.
   Everything from S3 to S5, computed.
4. **The parts list is the rocket.** Click through the tree: nose cone, body tube, inner tube, centering
   rings, fins, parachute, shock cord, rail buttons. Every part has a shape and a mass. Get the masses
   right and the CG is right. Get the shapes right and the CP is right.
   - **Pause card.** On screen: "The sim says the CG is here. My real rocket balances two inches further back. Which do I believe, and what do I fix?" Hold five seconds with a countdown, then a chime. On resume: Believe the rocket; a scale and a string do not guess. Fix the masses in the sim, part by part, until its CG matches the real one.
5. **Trust, but weigh.** The sim is only as good as what you typed in. After the build you will weigh your
   rocket and balance it (S3), and correct the file. Then the numbers mean something.

## Pause point
After beat 4. The card reads: "The sim says the CG is here. My real rocket balances two inches further back. Which do I believe, and what do I fix?"

On resume the video answers: Believe the rocket; a scale and a string do not guess. Fix the masses in the sim, part by part, until its CG matches the real one.

## Shot list
- The video is the segment: slides, pause card and answer card, see production.md.

## Check before showing
- OpenRocket version and where the CP/CG markers and stability readout sit in that version's layout.
- RockSim current price and version, if quoting them.
- BR-1.ork is current with the actual kit (white tube, current fin stock).

## Sources to replace
"Basics of OpenRocket" (youtu.be/z16_uUnMarE), linked from homework step 40.
