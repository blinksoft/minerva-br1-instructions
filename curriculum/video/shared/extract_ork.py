#!/usr/bin/env python3
"""Pull the numbers the videos quote out of the program's OpenRocket file, files/BR-1.ork.

    python3 curriculum/video/shared/extract_ork.py

Writes shared/br1-sim.json: the rocket's geometry and masses, the motors it is configured with, the
stored simulation results (OpenRocket saves them in the file), and a thinned time series of altitude,
speed, mass, CG, CP, stability margin and thrust. Run it again whenever BR-1.ork changes and commit.
"""
import json, math, os, zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ORK = os.path.join(ROOT, "files", "BR-1.ork")


def num(el, tag, default=None):
    x = el.find(tag)
    if x is None or x.text is None:
        return default
    try:
        return float(x.text.split()[-1])   # "auto 0.041656" -> 0.041656
    except ValueError:
        return x.text


def main():
    with zipfile.ZipFile(ORK) as z:
        xml = z.read([n for n in z.namelist() if n.endswith(".ork")][0])
    root = ET.fromstring(xml)
    rocket = root.find("rocket")
    nose = rocket.find(".//nosecone"); body = rocket.find(".//bodytube"); fins = rocket.find(".//trapezoidfinset")
    mount = rocket.find(".//innertube"); chute = rocket.find(".//parachute")
    geom = {
        "noseLengthM": num(nose, "length"), "noseShape": nose.findtext("shape"),
        "bodyLengthM": num(body, "length"), "bodyRadiusM": num(body, "radius"),
        "finCount": int(num(fins, "fincount")), "finRootM": num(fins, "rootchord"), "finTipM": num(fins, "tipchord"),
        "finHeightM": num(fins, "height"), "finSweepM": num(fins, "sweeplength"), "finThicknessM": num(fins, "thickness"),
        "finTabLengthM": num(fins, "tablength"), "finTabHeightM": num(fins, "tabheight"),
        "finOffsetFromBottomM": -num(fins, "axialoffset", 0.0),
        "motorMountLengthM": num(mount, "length"), "motorMountInnerRadiusM": num(mount, "outerradius") - num(mount, "thickness"),
        "parachute": chute.findtext("name") if chute is not None else None,
    }
    geom["totalLengthM"] = geom["noseLengthM"] + geom["bodyLengthM"]
    geom["bodyDiameterM"] = 2 * geom["bodyRadiusM"]
    masses = {}
    for el in rocket.iter():
        nm = el.findtext("name")
        if nm and (el.find("overridemass") is not None or el.find("mass") is not None):
            masses[nm] = masses.get(nm, 0) + (num(el, "overridemass") or num(el, "mass") or 0)
    motors = []
    for m in rocket.iter("motor"):
        motors.append({"configId": m.get("configid"), "manufacturer": m.findtext("manufacturer"),
                       "designation": m.findtext("designation"), "delayS": num(m, "delay"),
                       "diameterM": num(m, "diameter"), "lengthM": num(m, "length")})
    sims = []
    for s in root.iter("simulation"):
        cond = s.find("conditions"); fd = s.find("flightdata"); br = fd.find("databranch") if fd is not None else None
        sim = {"name": s.findtext("name"), "motorConfigId": cond.findtext("configid"),
               "motor": next((m["designation"] for m in motors if m["configId"] == cond.findtext("configid")), None),
               "conditions": {"launchRodLengthM": num(cond, "launchrodlength"), "launchRodAngleDeg": num(cond, "launchrodangle"),
                              "windAverageMs": num(cond, "windaverage"), "launchAltitudeM": num(cond, "launchaltitude"),
                              "latitude": num(cond, "launchlatitude"), "longitude": num(cond, "launchlongitude")},
               "summary": {k: float(v) for k, v in (fd.attrib.items() if fd is not None else [])},
               "events": [{"time": float(e.get("time")), "type": e.get("type")} for e in (br.iter("event") if br is not None else [])]}
        if br is not None:
            types = br.get("types").split(",")
            want = {"Time": "t", "Altitude": "altitudeM", "Total velocity": "speedMs", "Total acceleration": "accelMs2",
                    "Lateral distance": "lateralM", "Mass": "massKg", "Motor mass": "motorMassKg", "CP location": "cpM",
                    "CG location": "cgM", "Stability margin calibers": "stabilityCal", "Thrust": "thrustN",
                    "Thrust-to-weight ratio": "thrustToWeight", "Angle of attack": "aoaRad", "Mach number": "mach"}
            idx = {want[t]: i for i, t in enumerate(types) if t in want}
            rows = []
            last_t = -1
            for dp in br.iter("datapoint"):
                v = dp.text.split(",")
                t = float(v[idx["t"]])
                step = 0.1 if t < 15 else 1.0
                if t - last_t < step - 1e-9:
                    continue
                last_t = t
                row = {}
                for k, i in idx.items():
                    x = float(v[i])
                    row[k] = None if math.isnan(x) else round(x, 4)
                rows.append(row)
            # The design window's CP: zero angle of attack at Mach 0.3 (OpenRocket's default reference).
            # The flight's own CP wanders forward whenever the rocket is at an angle of attack, which is
            # why the first in-flight sample reads a lower margin than the design window shows.
            cands = [r for r in rows if r["cpM"] is not None and r["mach"] is not None and 0.25 <= r["mach"] <= 0.35]
            design_cp = min(cands, key=lambda r: r["aoaRad"])["cpM"] if cands else None
            d = geom["bodyDiameterM"]
            for r in rows:
                r["marginCal"] = round((design_cp - r["cgM"]) / d, 3) if design_cp and r["cgM"] is not None else None
                r["aoaDeg"] = round(math.degrees(r.pop("aoaRad")), 2) if r["aoaRad"] is not None else None
            sim["series"] = rows
            sim["design"] = {"cpM": design_cp, "cgM": rows[0]["cgM"], "massKg": rows[0]["massKg"],
                             "stabilityCal": round((design_cp - rows[0]["cgM"]) / d, 3) if design_cp else None,
                             "note": "what the design window shows for this configuration: CP at zero angle of attack, Mach 0.3"}
            first = next((r for r in rows if r["cpM"] is not None), None)
            sim["onPad"] = {"massKg": rows[0]["massKg"], "motorMassKg": rows[0]["motorMassKg"], "cgM": rows[0]["cgM"],
                            "cpM": first and first["cpM"], "stabilityCal": first and first["stabilityCal"]}
            burnout = next((e["time"] for e in sim["events"] if e["type"] == "burnout"), None)
            if burnout:
                rb = min(rows, key=lambda r: abs(r["t"] - burnout))
                sim["atBurnout"] = {"t": rb["t"], "massKg": rb["massKg"], "cgM": rb["cgM"], "cpM": rb["cpM"], "stabilityCal": rb["stabilityCal"]}
        sims.append(sim)
    # a slow flight (the G74) never reaches Mach 0.3; give it the design CP the faster runs found
    global_cp = next((s["design"]["cpM"] for s in sims if s.get("design", {}).get("cpM")), None)
    d = geom["bodyDiameterM"]
    for sim in sims:
        if sim.get("design") and not sim["design"]["cpM"] and global_cp:
            sim["design"]["cpM"] = global_cp
            sim["design"]["stabilityCal"] = round((global_cp - sim["design"]["cgM"]) / d, 3)
            for r in sim["series"]:
                r["marginCal"] = round((global_cp - r["cgM"]) / d, 3) if r["cgM"] is not None else None
    # empty rocket: remove each configuration's motor from its on-pad CG; the motor sits at the aft end of the mount
    mount_aft = geom["totalLengthM"] - abs(num(mount, "axialoffset", 0.0))
    empties = []
    for sim in sims:
        mo = next((m for m in motors if m["configId"] == sim["motorConfigId"]), None)
        if mo and sim.get("onPad"):
            mm, M, cg = sim["onPad"]["motorMassKg"], sim["onPad"]["massKg"], sim["onPad"]["cgM"]
            x_motor = mount_aft - mo["lengthM"] / 2
            empties.append(((M * cg - mm * x_motor) / (M - mm), M - mm))
    empty = None
    if empties:
        cg_e = sum(e[0] for e in empties) / len(empties); m_e = empties[0][1]
        cp = next((s["design"]["cpM"] for s in sims if s.get("design", {}).get("cpM")), None)
        empty = {"massKg": round(m_e, 3), "cgM": round(cg_e, 3),
                 "stabilityCal": round((cp - cg_e) / geom["bodyDiameterM"], 2) if cp else None,
                 "note": "estimated by removing each configuration's motor from its on-pad CG; not stored in the file"}
    design = {"cpM": next((s["design"]["cpM"] for s in sims if s.get("design", {}).get("cpM")), None),
              "empty": empty,
              "configurations": [{"motor": s["motor"], "delayS": next((m["delayS"] for m in motors if m["configId"] == s["motorConfigId"]), None),
                                  **{k: v for k, v in s["design"].items() if k != "note"}} for s in sims if s.get("design")]}
    out = {"source": "files/BR-1.ork (OpenRocket 24.12), stored simulation results", "designer": rocket.findtext("designer"),
           "design": design,
           "units": "metres, kilograms, seconds, Newtons; CG/CP measured from the nose tip",
           "geometry": geom, "massesKg": masses, "motors": motors, "simulations": sims}
    json.dump(out, open(os.path.join(HERE, "br1-sim.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("geometry", "massesKg", "motors")}, indent=1))
    for s in sims:
        print(s["name"], s["motor"], s["conditions"], s["summary"], s.get("onPad"), s.get("atBurnout"), len(s.get("series", [])), "rows")


if __name__ == "__main__":
    main()
