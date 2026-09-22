#!/usr/bin/env python3
"""Fetch certified thrust curves for the motors the program teaches with, from thrustcurve.org.

    python3 curriculum/video/shared/fetch_thrustcurves.py

Writes shared/thrustcurves.json in the shape the `curves` slide reads (same as S06/assets). Run it
once and commit the result; the slides never call the network.
"""
import json, os, sys, datetime, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://www.thrustcurve.org/api/v1/"
WANT = [("Estes", "A8"), ("AeroTech", "G12ST"), ("AeroTech", "G40W"), ("AeroTech", "G74W"),
        ("AeroTech", "HP-H115DM"), ("AeroTech", "H128W"), ("AeroTech", "HP-H135W"), ("AeroTech", "H180W")]


def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "ga-wing-br1-curriculum"})
    for attempt in range(6):          # TLS handshakes to the site time out now and then; just retry
        try:
            return json.load(urllib.request.urlopen(req, timeout=20))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt == 5:
                raise
            print("retrying", path, "after", e, file=sys.stderr)


def main():
    motors = []
    for manu, desig in WANT:
        r = post("search.json", {"manufacturer": manu, "designation": desig, "maxResults": 5})
        hits = [m for m in r.get("results", []) if m.get("designation") == desig] or r.get("results", [])
        if not hits:
            print("not found:", manu, desig, file=sys.stderr); continue
        m = hits[0]
        d = post("download.json", {"motorIds": [m["motorId"]], "format": "RASP", "data": "samples"})
        files = d.get("results", [])
        files.sort(key=lambda f: (f.get("source") != "cert", f.get("simfileId", 0)))
        if not files:
            print("no data file:", desig, file=sys.stderr); continue
        f = files[0]
        motors.append({
            "designation": m["designation"], "commonName": m.get("commonName"), "manufacturer": m["manufacturer"],
            "url": f"https://www.thrustcurve.org/motors/{m['manufacturer']}/{m['designation']}/",
            "impulseClass": m.get("impulseClass"), "diameterMm": m.get("diameter"), "lengthMm": m.get("length"),
            "totalWeightG": m.get("totalWeightG"), "propWeightG": m.get("propWeightG"),
            "delays": m.get("delays"), "certOrg": m.get("certOrg"), "type": m.get("type"),
            "avgThrustN": m.get("avgThrustN"), "maxThrustN": m.get("maxThrustN"),
            "totImpulseNs": m.get("totImpulseNs"), "burnTimeS": m.get("burnTimeS"),
            "propInfo": m.get("propInfo"), "dataSource": f.get("source"),
            "samples": [[round(s["time"], 4), round(s["thrust"], 4)] for s in f["samples"]],
        })
        print(f"{m['manufacturer']} {m['designation']}: {m.get('avgThrustN')} N avg, {m.get('totImpulseNs')} N·s, "
              f"{m.get('burnTimeS')} s, {len(f['samples'])} samples ({f.get('source')})")
    out = {"source": "thrustcurve.org API, RASP data files, public domain per the site's license field",
           "fetched": datetime.date.today().isoformat(), "motors": motors}
    json.dump(out, open(os.path.join(HERE, "thrustcurves.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
