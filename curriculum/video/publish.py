#!/usr/bin/env python3
"""Publish rendered segment videos to the program's YouTube channel.

    python3 publish.py --auth        one-time sign-in as the channel owner; stores a token
    python3 publish.py S06           publish one segment if its render changed
    python3 publish.py all           publish every rendered segment whose render changed
    python3 publish.py --status      show what is live
    python3 publish.py --thumbnails  (re)set the title-slide thumbnail on every live video, no re-upload

A segment is published when the rendered output (videos/SNN.mp4 + .srt) differs from what is live,
by content hash recorded in videos/youtube.json. Re-rendering is decided separately by render.py from
the inputs; an encode that produces identical bytes publishes nothing, so renderer or CI changes never
churn the channel. YouTube cannot replace a video's file, so publishing uploads a new video, sets the
thumbnail and captions, puts it in the playlist in segment order, deletes the superseded video, and
records the new ID in videos/youtube.json and curriculum/production.md.

Credentials (a .env file in the repo root is read too; keep it out of git):
    GOOGLE_AUTH_JSON     the OAuth "Desktop app" client JSON from Google Cloud, inline or a file path.
                         Default file: ~/.config/ga-wing-youtube/client_secret.json
    YOUTUBE_TOKEN_JSON   the token written by --auth, inline or a file path.
                         Default file: ~/.config/ga-wing-youtube/token.json
In GitHub Actions both come from repository secrets of the same names.

Quota: a new Google Cloud project allows about four full publishes a day. On quotaExceeded the script
stops cleanly and the nightly run finishes the rest.
"""
import datetime, hashlib, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VIDEOS = os.path.join(ROOT, "videos")
STATE = os.path.join(VIDEOS, "youtube.json")
PRODUCTION = os.path.join(ROOT, "curriculum", "production.md")
CONF_DIR = os.path.expanduser("~/.config/ga-wing-youtube")
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl", "https://www.googleapis.com/auth/youtube.upload"]
PLAYLIST_TITLE = "BR-1 Build Day"
PRIVACY = "unlisted"
CATEGORY_EDUCATION = "27"

sys.path.insert(0, HERE)
from render import load_env  # noqa: E402  (reads ROOT/.env)
load_env()


# ---------------------------------------------------------------- credentials

def _json_env(name, default_path):
    v = os.environ.get(name, "").strip()
    if v.startswith("{"):
        return json.loads(v)
    p = os.path.expanduser(v or default_path)
    return json.load(open(p)) if os.path.exists(p) else None


def client_config():
    cfg = _json_env("GOOGLE_AUTH_JSON", os.path.join(CONF_DIR, "client_secret.json"))
    if not cfg:
        sys.exit("No OAuth client JSON. Set GOOGLE_AUTH_JSON or save it to ~/.config/ga-wing-youtube/client_secret.json")
    return cfg


def _save_token(creds):
    os.makedirs(CONF_DIR, exist_ok=True)
    tok = os.path.join(CONF_DIR, "token.json")
    open(tok, "w").write(creds.to_json())
    os.chmod(tok, 0o600)
    print(f"Token saved to {tok}")
    print("For GitHub Actions run:\n  gh secret set YOUTUBE_TOKEN_JSON < " + tok)


def auth(redirect=None):
    """One-time sign-in.

    Default: prints a URL, listens on localhost:8765 for the redirect (ignoring stray browser requests).
    Fallback for machines where the browser cannot reach the terminal: run with --auth first, open the
    URL, and when the browser lands on a localhost page that fails to load, copy that page's full address
    and run  publish.py --auth --redirect "<that address>".
    """
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs
    from google_auth_oauthlib.flow import InstalledAppFlow
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"   # the redirect is http://localhost, which is the norm for desktop apps
    port = 8765
    pending = os.path.join(CONF_DIR, "pending-auth.json")
    if redirect:
        if not os.path.exists(pending):
            sys.exit("No pending sign-in. Run --auth first, then --redirect with the address the browser landed on.")
        pend = json.load(open(pending))
        flow = InstalledAppFlow.from_client_config(client_config(), SCOPES, redirect_uri=f"http://localhost:{port}/",
                                                   code_verifier=pend["code_verifier"], state=pend["state"])
        flow.fetch_token(authorization_response=redirect.strip())
        os.remove(pending)
        _save_token(flow.credentials); return

    flow = InstalledAppFlow.from_client_config(client_config(), SCOPES, redirect_uri=f"http://localhost:{port}/")
    url, state = flow.authorization_url(prompt="consent", access_type="offline")
    os.makedirs(CONF_DIR, exist_ok=True)
    json.dump({"state": state, "code_verifier": flow.code_verifier}, open(pending, "w"))
    os.chmod(pending, 0o600)
    print("\nOpen this URL in a browser, sign in as the channel owner, and approve.\n"
          "Google will warn that the app is unverified; that is expected for a private tool.\n")
    print(url + "\n")
    print("Waiting up to 5 minutes for the browser to come back to localhost:8765 ...\n"
          "If the browser shows 'refused to connect', copy the full address from its address bar and run:\n"
          "  publish.py --auth --redirect \"<that address>\"\n")
    got = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            if "code" in q and q.get("state", [None])[0] == state:
                got["url"] = f"http://localhost:{port}{self.path}"
                body = b"Signed in. You can close this tab."
            elif "error" in q:
                got["error"] = q["error"][0]
                body = ("Google returned: " + q["error"][0]).encode()
            else:
                self.send_response(404); self.end_headers(); return   # favicon, prefetch, wrong state
            self.send_response(200); self.send_header("Content-Type", "text/plain"); self.end_headers()
            self.wfile.write(body)

    srv = HTTPServer(("127.0.0.1", port), H)
    srv.timeout = 300
    deadline = time.time() + 300
    while not got and time.time() < deadline:
        srv.handle_request()
    srv.server_close()
    if not got:
        sys.exit("Timed out. The pending sign-in is kept: open the URL again or use --redirect.")
    if "error" in got:
        sys.exit(f"Sign-in failed: {got['error']}")
    flow.fetch_token(authorization_response=got["url"])
    os.remove(pending)
    _save_token(flow.credentials)


def service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    info = _json_env("YOUTUBE_TOKEN_JSON", os.path.join(CONF_DIR, "token.json"))
    if not info:
        sys.exit("No YouTube token. Run: python3 curriculum/video/publish.py --auth")
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------- helpers

def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"channel": "GA Wing AeroSpace and STEM Education, https://www.youtube.com/@GAWingAEO", "playlistId": None, "segments": {}}


def save_state(st):
    json.dump(st, open(STATE, "w"), indent=2)
    open(STATE, "a").write("\n")


def seg_number(seg):
    return int(re.sub(r"\D", "", seg) or 0)


def read_kit(seg):
    """Title, description and tags from videos/SNN.youtube.md written by render.py."""
    txt = open(os.path.join(VIDEOS, f"{seg}.youtube.md"), encoding="utf-8").read()
    def section(name):
        m = re.search(rf"^## {name}\n\n(.*?)(?=\n## |\Z)", txt, flags=re.S | re.M)
        return m.group(1).strip() if m else ""
    tags = [t.strip() for t in section("Tags").split(",") if t.strip()]
    return section("Title"), section("Description"), tags


def output_hash(seg):
    h = hashlib.sha1()
    for ext in (".mp4", ".srt"):
        p = os.path.join(VIDEOS, seg + ext)
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()


def is_quota(err):
    return getattr(err, "resp", None) is not None and err.resp.status == 403 and b"quota" in (err.content or b"").lower()


def ensure_playlist(yt, st):
    if st.get("playlistId"):
        return st["playlistId"]
    page = None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=page).execute()
        for p in r.get("items", []):
            if p["snippet"]["title"] == PLAYLIST_TITLE:
                st["playlistId"] = p["id"]; save_state(st); return p["id"]
        page = r.get("nextPageToken")
        if not page:
            break
    r = yt.playlists().insert(part="snippet,status", body={
        "snippet": {"title": PLAYLIST_TITLE,
                    "description": "Short teaching segments that fill the epoxy cure waits during the "
                                   "Georgia Wing High Power Rocketry Minerva BR-1 build day."},
        "status": {"privacyStatus": PRIVACY}}).execute()
    st["playlistId"] = r["id"]; save_state(st)
    print(f"created playlist '{PLAYLIST_TITLE}' {r['id']}")
    return r["id"]


def upload_video(yt, seg, title, description, tags):
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(os.path.join(VIDEOS, f"{seg}.mp4"), mimetype="video/mp4",
                            chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body={
        "snippet": {"title": title[:100], "description": description[:5000], "tags": tags[:30],
                    "categoryId": CATEGORY_EDUCATION, "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": False, "embeddable": True}},
        media_body=media)
    resp, retries = None, 0
    while resp is None:
        try:
            status, resp = req.next_chunk()
            if status:
                print(f"  {seg}: uploading {int(status.progress() * 100)}%", end="\r")
        except Exception as e:  # transient network errors on a resumable upload
            retries += 1
            if retries > 6 or is_quota(e):
                raise
            time.sleep(2 ** retries)
    print(f"  {seg}: uploaded as {resp['id']}                    ")
    return resp["id"]


def set_thumbnail(yt, seg, video_id):
    from googleapiclient.http import MediaFileUpload
    p = os.path.join(VIDEOS, f"{seg}-thumb.jpg")
    if not os.path.exists(p):
        return
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(p, mimetype="image/jpeg")).execute()
        return True
    except Exception as e:
        if is_quota(e):
            raise
        print(f"  {seg}: thumbnail not set ({str(e)[:90]}). Custom thumbnails need a phone-verified channel.")
        return False


def set_captions(yt, seg, video_id):
    from googleapiclient.http import MediaFileUpload
    p = os.path.join(VIDEOS, f"{seg}.srt")
    if not os.path.exists(p):
        return
    yt.captions().insert(part="snippet", body={"snippet": {"videoId": video_id, "language": "en", "name": "English"}},
                         media_body=MediaFileUpload(p, mimetype="application/octet-stream")).execute()


def add_to_playlist(yt, playlist_id, seg, video_id, st):
    position = sum(1 for k, v in st["segments"].items() if v.get("videoId") and seg_number(k) < seg_number(seg))
    yt.playlistItems().insert(part="snippet", body={"snippet": {
        "playlistId": playlist_id, "position": position,
        "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()


def update_production_table(seg, video_id):
    if not os.path.exists(PRODUCTION):
        return
    s = open(PRODUCTION, encoding="utf-8").read()
    label = f"S{seg_number(seg)}"
    today = datetime.date.today().isoformat()
    def repl(m):
        cells = [c.strip() for c in m.group(0).strip().strip("|").split("|")]
        # #, Title, Voice, YouTube ID, Master file, Recorded
        while len(cells) < 6:
            cells.append("")
        cells[3] = video_id; cells[4] = f"videos/{seg}.mp4"; cells[5] = f"published {today}"
        return "| " + " | ".join(cells) + " |"
    s2 = re.sub(rf"^\| {label} \|.*$", repl, s, count=1, flags=re.M)
    if s2 != s:
        open(PRODUCTION, "w", encoding="utf-8").write(s2)


# ---------------------------------------------------------------- publish

def publish(segs):
    from googleapiclient.errors import HttpError
    yt = service()
    st = load_state()
    playlist_id = ensure_playlist(yt, st)
    for seg in segs:
        sha_p = os.path.join(VIDEOS, f"{seg}.sha")
        if not os.path.exists(sha_p) or not os.path.exists(os.path.join(VIDEOS, f"{seg}.mp4")):
            print(f"{seg}: not rendered, skipped"); continue
        sha = open(sha_p).read().strip()
        out_sha = output_hash(seg)
        cur = st["segments"].get(seg, {})
        if cur.get("videoId") and cur.get("outputSha") == out_sha:
            print(f"{seg}: output unchanged, live as {cur['videoId']}"); continue
        title, description, tags = read_kit(seg)
        old_id = cur.get("videoId")
        try:
            vid = upload_video(yt, seg, title, description, tags)
            st["segments"][seg] = {"videoId": vid, "outputSha": out_sha, "inputSha": sha, "title": title, "url": f"https://youtu.be/{vid}",
                                   "publishedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                                   "previousVideoId": old_id}
            save_state(st)                      # record the new ID before anything else can fail
            set_thumbnail(yt, seg, vid)
            set_captions(yt, seg, vid)
            add_to_playlist(yt, playlist_id, seg, vid, st)
            if old_id:
                try:
                    yt.videos().delete(id=old_id).execute()
                    print(f"  {seg}: deleted superseded video {old_id}")
                except HttpError as e:
                    if is_quota(e):
                        raise
                    print(f"  {seg}: could not delete old video {old_id} ({e.resp.status})")
            status = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]["privacyStatus"]
            st["segments"][seg]["privacyStatus"] = status
            save_state(st)
            update_production_table(seg, vid)
            note = "" if status == PRIVACY else f"  NOTE: YouTube set it to '{status}'. Until the API project passes Google's audit, flip it to Unlisted in YouTube Studio."
            print(f"{seg}: published https://youtu.be/{vid} ({status}){note}")
        except HttpError as e:
            if is_quota(e):
                print(f"{seg}: YouTube API quota exhausted for today; the nightly run will continue from here.")
                return 0
            print(f"{seg}: YouTube error {e.resp.status}: {e.content[:300]}")
            return 1
    return 0


def refresh_thumbnails():
    yt = service()
    st = load_state()
    for seg in sorted(st["segments"], key=seg_number):
        vid = st["segments"][seg].get("videoId")
        if vid and set_thumbnail(yt, seg, vid):
            print(f"{seg}: thumbnail set on {vid}")


def status():
    st = load_state()
    print(f"playlist: {st.get('playlistId')}")
    for seg in sorted(st["segments"], key=seg_number):
        v = st["segments"][seg]
        state = "current" if output_hash(seg) == v.get("outputSha") else "output changed, republish pending"
        print(f"{seg}: {v.get('url')}  {v.get('privacyStatus', '?')}  {state}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--auth" in sys.argv:
        r = sys.argv[sys.argv.index("--redirect") + 1] if "--redirect" in sys.argv else None
        auth(r); sys.exit(0)
    if "--status" in sys.argv:
        status(); sys.exit(0)
    if "--thumbnails" in sys.argv:
        refresh_thumbnails(); sys.exit(0)
    if not args:
        sys.exit(__doc__)
    if args[0] == "all":
        args = sorted((f[:-4] for f in os.listdir(VIDEOS) if re.fullmatch(r"S\d+\.sha", f)), key=seg_number)
    sys.exit(publish(args))
