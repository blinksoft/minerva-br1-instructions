#!/usr/bin/env python3
"""Cut screen-recording clips for a segment from the raw recordings.

    python3 shared/cut_clips.py S11 [S12 ...]

Reads SNN/assets/clips.json:
    {"sources": {"A": "recordings/2026-09-21_23-32-57.mp4", ...},        # relative to the repo root
     "clips":   {"02-new.mp4": [["A", 2.0, 17.0], ["A", 24.0, 40.0]], ...}}   # ranges in seconds, in order

Each clip is the ranges joined in order, re-encoded at 30 fps with no audio, written to SNN/assets/.
The raw recordings are not part of the repo; the clips are. Re-run only when a range changes."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(VIDEO))


def ffmpeg():
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        import shutil
        return shutil.which("ffmpeg") or sys.exit("ffmpeg not found")


def cut(seg):
    adir = os.path.join(VIDEO, seg, "assets")
    spec = json.load(open(os.path.join(adir, "clips.json")))
    ff = ffmpeg()
    for name, ranges in spec["clips"].items():
        cmd = [ff, "-y", "-v", "error"]
        parts = []
        for i, (src, a, b) in enumerate(ranges):
            path = os.path.join(ROOT, spec["sources"][src])
            if not os.path.exists(path):
                sys.exit(f"{seg}: recording not found: {path}")
            cmd += ["-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", path]
            parts.append(f"[{i}:v]fps=30,setsar=1[v{i}]")
        graph = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(ranges))) + f"concat=n={len(ranges)}:v=1:a=0[out]"
        out = os.path.join(adir, name)
        cmd += ["-filter_complex", graph, "-map", "[out]", "-an",
                "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)
        print(f"{seg}/assets/{name}: {sum(b - a for _, a, b in ranges):.0f} s, {os.path.getsize(out) / 1e6:.1f} MB")


if __name__ == "__main__":
    for s in sys.argv[1:] or sys.exit(__doc__):
        cut(s)
