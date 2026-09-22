# S10 — Why simulate, and what tools exist: narration script

Record one file per numbered cue, as `voice/NN.wav` (any sample rate, mono is fine).
Leave a beat of silence at the start and end of each. Re-run render.py and the slides
re-time themselves to your voice.

**01** `voice/01.wav`

Segment ten. Why simulate, and what tools exist. By the end of this you will be able to say why the program simulates before it flies, name the two common tools, and recognize the CG and CP markers and the stability number in OpenRocket.

**02** `voice/02.wav`

A flight is a test you only get to run once. A simulator flies your rocket as numbers on a screen, a hundred times before you fly it once for real. This is the BR-1 you are building right now, flown by OpenRocket on a G74W-6, the motor most of you will fly. It says stable. It says about seven hundred feet, two hundred and ten meters on the G, and about twenty-one hundred, six hundred and forty meters on the H. It says how fast it leaves the rail and which delay to buy. Segment twelve reads those numbers off the screen.

**03** `voice/03.wav`

There are two common tools. OpenRocket is free and open source, so anyone can read and improve the code. It runs on Windows, Mac and Linux. RockSim, from Apogee Components, is the paid alternative, with a longer history and some extra features. Both answer the same questions. Is it stable, how high, how fast, which delay. The program uses OpenRocket and gives you its BR-1 file, so you never start from a blank screen.

**04** `voice/04.wav`

Open the file. This is the BR-1 in OpenRocket, as built, with an H115 loaded. OpenRocket draws two dots on it. The blue dot is the CG, the center of gravity, the balance point: twenty-seven and a half inches, six hundred and ninety-eight millimeters from the nose tip. The red dot is the CP, the center of pressure, where the push of the air adds up: thirty-three and three quarter inches, eight hundred and fifty-eight millimeters. The number in the top corner is the stability margin, the gap between them in calibers, body widths. With the H in, two point zero. Switch the flight configuration to the G74 and it reads two and a half. Segments three, four and five, computed in a blink.

**05** `voice/05.wav`

Where do those dots come from. From the parts list. Every part in the kit is a line in this tree. Nose cone, body tube, motor mount, centering rings, fins, parachute, shock cord, rail buttons. Every part has a shape and a mass.

**06** `voice/06.wav`

Here is the tree, with the masses the file carries. Nose cone, eight and a half ounces, two hundred and forty grams. Body tube, twelve and a half, three hundred and fifty-four grams. Motor mount, about one. The rings, fins and parachute have no number typed in. OpenRocket weighs them from their shape and material. Whole rocket, about two pounds two ounces, nine hundred and fifty-eight grams without a motor. Get the masses right and the CG is right. Get the shapes right and the CP is right.

**07 — pause card, no narration.** The card reads: _The sim says the CG is here. My real rocket balances two inches further back. Which do I believe, and what do I fix?_

**08** `voice/08.wav`

Believe the rocket. A scale and a string do not guess. Fix the masses in the sim, part by part, until its CG matches the real one. Now stretch that. Two inches further back means the real rocket is heavier toward the tail than the file thinks. Look for what the file is missing. Epoxy fillets, paint, the hydro-dip on the nose cone. Put those masses in where they really sit. The CG moves back toward the CP, the margin shrinks, and now the number on the screen tells the truth.

**09** `voice/09.wav`

One last thing. Trust, but weigh. The sim is only as good as what you typed in. After the build you will weigh your rocket and balance it on a finger, as in Segment three. Then you correct the file until it agrees. That is Segment twelve, and only then do the numbers mean something. Before that, Segment eleven builds this same tree from a blank screen.

**10** `voice/10.wav`

The one thing to remember. Simulate before you fly. And the sim is only as true as what you typed in.
