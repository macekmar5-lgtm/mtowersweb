"""Málaga Towers: photoreal stills from the 3D camera frames with Nano Banana Pro (Gemini 3 Pro Image).

Image 1 is always the 3D camera frame exports/still-<view>-sunset.png (the composition lock); images 2..14 are the
per-view references below. Variants are generated at 2K into media/candidates/; a picked variant is re-run at 4K
(--final) or simply promoted as is (--promote).

  python gen_stills.py front                      3 variants of the front view at 2K
  python gen_stills.py side back --variants 4     4 variants each
  python gen_stills.py all                        every view
  python gen_stills.py front --dry-run            print images + prompt + cost, no API call, no cost
  python gen_stills.py --final front_2            re-run candidate front_2 (same prompt, images, seed) at 4K
  python gen_stills.py --promote front_2          use the 2K candidate front_2 as media/front.jpg (no API call)
  python gen_stills.py --sheet front              rebuild the contact sheet only
  python gen_stills.py --list-models              list the image models this API key can use (free)

API key: env GEMINI_API_KEY, else .env next to this file (asked once and saved there). Never hard-coded.
Money: every paid run prints its cost and asks before calling the API (unless --yes); runs over $5 always ask.
"""
import argparse, csv, datetime, getpass, hashlib, io, json, os, random, sys, time
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is missing: run  py -m pip install pillow google-genai  (or use GEN-STILLS.bat)")

ROOT = Path(__file__).resolve().parent
EXPORTS, REFS, MEDIA = ROOT / "exports", ROOT / "refs", ROOT / "media"
CAND = MEDIA / "candidates"
LOG = CAND / "log.csv"
ENV = ROOT / ".env"

MODEL = "gemini-3-pro-image"                 # Nano Banana Pro, as listed in AI Studio
MODEL_FALLBACK = "gemini-3-pro-image-preview"  # id used in parts of the Gemini 3 docs; tried automatically on 404
PRICE = {"2K": 0.134, "4K": 0.24}            # USD per output image (ai.google.dev/gemini-api/docs/pricing, Nov 2026)
PRICE_INPUT_IMAGE = 0.0011                   # 560 tokens at $2 / 1M
CONFIRM_ABOVE = 5.0
MAX_IMAGES = 14                              # "Maximum images per prompt: 14"
VIEWS = ["front", "side", "back", "rooftop", "aerial"]

# Per-view references, most important first. v2 (after the first front test, 16 Nov 2026): ONLY photos taken from
# the same angle as the view, plus close-up material details. Elevated/oblique drone shots in the front list hijacked
# the camera in all 3 variants, so any reference whose viewpoint differs from the view is left out. Names are
# file-name prefixes (refs/video, refs/full, refs/user, then refs/preview).
REF_LISTS = {
    "front": ["v3_4k_front_from_sea_golden_hour", "v3_4k_front_from_sea_day", "v3_4k_front_from_sea_blue_hour",
              "sv_01_tower_base_street", "v3_4k_entrance_92_dusk", "02_detail_white_plates",
              "03_detail_corner_stack", "20_detail_plates_from_below"],
    "side": ["19_photo_promenade", "sv_01_tower_base_street", "v3_4k_entrance_92_dusk", "12_photo_facade_up",
             "02_detail_white_plates", "03_detail_corner_stack", "20_detail_plates_from_below"],
    "back": ["v1_render_three_towers_from_city", "v3_4k_podium_pool_garden", "v1_render_garden_pond",
             "sv_01_tower_base_street", "02_detail_white_plates", "03_detail_corner_stack", "20_detail_plates_from_below"],
    "rooftop": ["v3_4k_rooftop_pool_coast", "v3_4k_rooftop_pool_2", "08_rooftop_pool_sunset",
                "v3_4k_sunset_coast_chimney_port", "02_detail_white_plates", "03_detail_corner_stack"],
    "aerial": ["v1_drone_oblique_promenade", "v1_drone_from_sea_warehouses", "v3_4k_drone_oblique_beach_road_1",
               "sv_01_tower_base_street", "02_detail_white_plates", "03_detail_corner_stack", "20_detail_plates_from_below"],
}

# ---------------------------------------------------------------- prompt blocks
# v2: edit-style lock + the measured layout of Image 1 + only what is visible in that view (listing landmarks that are
# outside the frame made the model move the camera to show them). Facts per HANDOFF §5 as corrected in §13.
LOCK = ("Turn Image 1 into a photorealistic photograph. Image 1 is an untextured 3D render of the real site and it fixes "
        "the exact composition: keep the same camera position, height, angle, lens and framing, the same horizon "
        "height, and keep every building, tree line, road, beach and landmark at the same position, size and outline. "
        "Do not move the camera. Do not move, add or remove buildings, do not change the number of floors, and do not "
        "add any landmark that is not in Image 1. Only replace the flat 3D surfaces with real materials, light and detail.")
FRAME = {  # measured from the 3D camera (projected tower boxes), see index.html VIEWS
    "front": ("Layout of Image 1 to keep: a low long-lens view from the sea. Calm sea fills the bottom 40% of the frame; a "
              "thin strip of beach crosses the whole width at about 60–64% height. The three towers stand side by side "
              "in one straight row: left tower at 21–36% of the width, middle tower at 45–59%, right tower at 66–81%, "
              "all with their roofs about 12% below the top edge and their bases hidden behind trees at about 57%."),
    "side": ("Layout of Image 1 to keep: an eye-level view, camera 2 m above the paving, looking along the coast. The paved "
             "plaza fills the bottom quarter and the horizon is at about 72% height. The towers are on the left: the "
             "nearest at 9–32% of the width with its roof 11% below the top edge, the second partly behind it at 26–41%, "
             "the third smaller at 36–47%. The right half of the frame is open sky above the beach and the promenade."),
    "back": ("Layout of Image 1 to keep: a drone view from the city side at about 80 m height, looking down toward the sea. "
             "The sea horizon is a straight line about 23% from the top. The three towers stand in a row at 7–27%, 35–50% "
             "and 60–77% of the width, roofs 26% from the top, bases at about 76%. Gardens and low buildings fill the "
             "bottom quarter."),
    "rooftop": ("Layout of Image 1 to keep: standing on the timber roof deck about 75 m above the ground, looking out over "
                "the bay. The sea horizon is about 33% from the top. The deck and the long pool fill the bottom right; the "
                "glass balustrade with its dark handrail crosses the frame; the beach, promenade and road run from the "
                "bottom-left corner toward the chimney near the left edge; open sea fills the centre and right."),
    "aerial": ("Layout of Image 1 to keep: an oblique drone view from about 70 m above the beach in front of the towers, "
               "looking slightly down. The mountains on the horizon are about 14% from the top. The three towers stand at "
               "22–38%, 46–61% and 66–82% of the width with their roofs about 11% below the top edge and their bases at "
               "54–60%. The road crosses the frame just below the towers; the promenade and beach fill the bottom third."),
}
REFS_LINE = ("Images 2–{last} are photographs of the same towers, used ONLY for materials and details: the white plates, "
             "glass, balustrades and the base with its posts. Ignore their camera angles, framing and surroundings.")
BUILDING = ("Málaga Towers by Estudio Lamela: three identical residential towers, each with exactly the number of floors "
            "shown in Image 1 (21 residential floors above the base). Every floor is ringed by thick bright-white "
            "cantilevered slab plates about one metre deep; their projection changes from floor to floor and from "
            "segment to segment, so each outline is a jagged stack of white bands with deep shadow beneath every plate, "
            "never neat identical rings. Frameless clear glass balustrades on every plate; recessed dark grey-blue "
            "floor-to-ceiling glazing; grey horizontal-slat louvre panels in some bays. The base: a recessed dark-glass "
            "ground floor under a deep white overhang, then a wide continuous white band with a row of straight vertical "
            "white posts. Flat roof with a dark graphite plant room.")
VISIBLE = {
    "front": ("Visible, exactly where Image 1 shows it: in the gaps between the towers, set back behind them, modern 7–8 "
              "storey apartment blocks with dark glazing and white horizontal balcony bands; the "
              "city and low mountains far behind; palms and trees along the promenade; a white beach bar with straw "
              "umbrellas on the sand in front of the gap between the middle and the right tower; a wide golden beach "
              "with no palm trees on the open sand; calm sea in the foreground."),
    "side": ("Visible, exactly where Image 1 shows it: the wide light-grey paved promenade plaza with rows of tall palm "
             "trees and tall white lamp posts; the road with trees on the left; the golden beach on the right; the tall "
             "pale-brick Los Guindos chimney small in the distance just right of centre; low mountains on the horizon."),
    "back": ("Visible, exactly where Image 1 shows it: gardens with trees and low white apartment blocks in the foreground; "
             "two modern 7–8 storey blocks with dark glazing and white balcony bands just behind the towers; white stepped "
             "pergolas and podium roofs with pools between "
             "the towers; large warehouse roofs on the left; the inland road and an empty sandy lot on the right; beyond "
             "the towers the coast road, the promenade, the golden beach, a stone breakwater on the right and the open sea."),
    "rooftop": ("Visible, exactly where Image 1 shows it: the timber deck and the long infinity pool in the foreground and "
                "a frameless glass balustrade with a dark metal handrail; far below, the promenade, road, warehouses and "
                "beach running along the coast to the tall pale-brick Los Guindos chimney; on the horizon the bay of "
                "Málaga, the port cranes and the coastal mountains; open calm sea."),
    "aerial": ("Visible, exactly where Image 1 shows it: the six-lane road with a tree median; the wide promenade with red "
               "paving, lawns, white shade pergolas and the seaside walkway; low dunes with a few palm clusters; a white "
               "beach bar with straw umbrellas; the roundabout and an inland road with an empty sandy lot on the left; "
               "warehouses with blue-grey roofs on the right; the dense city and the mountains behind."),
}
# v3: the real golden-hour photo (v3_4k_front_from_sea_golden_hour) has the sea-facing facades lit warm gold; "raking
# across the west-facing faces" left them in cool shade in the front tests.
LIGHT = ("Golden hour a few minutes before sunset: a low warm sun from the west-south-west lights the sea-facing "
         "facades and the white plates a warm golden apricot, with a crisp dark shadow under every plate; faces turned "
         "away from the sun are soft cool blue; clear pale-blue sky warming to peach near the horizon, soft haze over "
         "the sea. Photoreal architectural photograph, natural colour, crisp detail, no people in focus, no text or "
         "logos, 16:9.")
CONSISTENCY = ("The last image (Image {n}) is the approved hero shot of this project: match its colour grade, light and "
               "materials exactly. Do not copy its composition.")
# The camera is ON one tower here: the generic "three towers" text made the model insert towers into the sea.
ROOFTOP_BUILDING = ("This is the roof terrace of one of the Málaga Towers by Estudio Lamela; the camera stands on it. No "
                    "other tall tower is in view: do not add any building where Image 1 shows sky or sea. Timber deck of "
                    "warm teak-coloured boards, a long rectangular infinity pool with clear turquoise water and a dark "
                    "mosaic edge, frameless clear glass balustrade panels with a slim dark metal handrail, the white "
                    "edge of the roof slab just below the balustrade.")

# Test results 16 Nov 2026 (media/candidates/log.csv): with ANY reference photo after the camera frame, even one shot
# from the same angle, Nano Banana Pro abandoned Image 1's composition (wrong camera, 9–16 floors). With the camera
# frame alone, all views kept the composition. So references are opt-in (--max-refs N) and the lists above are kept
# for experiments only.
DEFAULT_MAX_REFS = 0
QA = ["Composition matches Image 1 (flick between them; the towers sit in the same pixels).",
      "21 floors + base on every tower, and the base looks like sv_01 (dark recessed ground floor, white band with posts).",
      "Plates are irregular and staggered, not neat rings.",
      "No palms on open sand; the beach bar is there; the warehouses are next to the towers.",
      "No logos, no text, no invented extra towers or landmarks that are not in Image 1.",
      "Sunset light consistent with the approved front."]


# ---------------------------------------------------------------- helpers
def find_ref(name):
    """Resolve a reference by file-name prefix; refs/full falls back to refs/preview."""
    for sub in ("video", "full", "user", "preview"):
        hits = sorted((REFS / sub).glob(name + "*"))
        hits = [h for h in hits if h.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
        if hits:
            return hits[0]
    return None


def camera_frame(view):
    return EXPORTS / f"still-{view}-sunset.png"


def build_request(view, max_refs=DEFAULT_MAX_REFS, ref_names=None, use_hero=False):
    """Return (list of (label, path), prompt, warnings). Default: the camera frame only (see DEFAULT_MAX_REFS)."""
    warn = []
    frame = camera_frame(view)
    if not frame.exists():
        raise SystemExit(f"Camera frame missing: {frame}. Export it from index.html?dev first.")
    hero = MEDIA / "front.jpg"
    consistency = use_hero and view != "front" and hero.exists()
    room = MAX_IMAGES - 1 - (1 if consistency else 0)
    if max_refs is not None:
        room = min(room, max_refs)
    refs = []
    for name in (ref_names if ref_names is not None else REF_LISTS[view]):
        p = find_ref(name)
        if p is None:
            warn.append(f"reference not found, skipped: {name}")
            continue
        refs.append((name, p))
    refs = refs[:room]
    images = [("camera frame (3D layout)", frame)] + refs
    if consistency:
        images.append(("approved hero shot", hero))
    n = len(images)
    parts = [LOCK, FRAME[view]]
    last_ref = n - 1 if consistency else n
    if last_ref >= 2:
        parts.append(REFS_LINE.format(last=last_ref))
    parts += [ROOFTOP_BUILDING if view == "rooftop" else BUILDING, VISIBLE[view], LIGHT]
    if consistency:
        parts.append(CONSISTENCY.format(n=n))
    return images, "\n\n".join(parts), warn


def image_part(path, is_frame, types):
    """Camera frame goes in lossless; references are downscaled JPEGs (keeps the request well under 20 MB)."""
    im = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    if is_frame:
        im.save(buf, "PNG")
        return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
    im.thumbnail((1600, 1600), Image.LANCZOS)
    im.save(buf, "JPEG", quality=90)
    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")


def load_key(interactive=True):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key and ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key and interactive:
        key = getpass.getpass("Gemini API key (input hidden; saved to .env next to gen_stills.py): ").strip()
        if key:
            ENV.write_text(f"GEMINI_API_KEY={key}\n", encoding="utf-8")
            gi = ROOT / ".gitignore"
            lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
            if ".env" not in lines:
                gi.write_text("\n".join(lines + [".env"]) + "\n", encoding="utf-8")
            print(f"Saved to {ENV} (listed in .gitignore).")
    if not key:
        sys.exit("No API key. Set GEMINI_API_KEY or run again and paste it when asked.")
    return key


def next_index(view):
    nums = [int(p.stem.rsplit("_", 1)[1]) for p in CAND.glob(f"{view}_*.png") if p.stem.rsplit("_", 1)[1].isdigit()]
    return max(nums, default=0) + 1


def spent_so_far():
    if not LOG.exists():
        return 0.0
    with LOG.open(encoding="utf-8") as f:
        return sum(float(r.get("cost_usd") or 0) for r in csv.DictReader(f) if r.get("status") == "ok")


LOG_FIELDS = ["time", "view", "file", "size", "model", "seed", "prompt_sha", "images", "status", "cost_usd",
              "prompt_tokens", "output_tokens", "thought_tokens", "out_w", "out_h", "note"]


def log_row(**kw):
    CAND.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: kw.get(k, "") for k in LOG_FIELDS})


def confirm(total, assume_yes):
    print(f"\nEstimated cost of this run: ${total:.2f}   (logged so far: ${spent_so_far():.2f})")
    if assume_yes and total <= CONFIRM_ABOVE:
        return
    msg = "This run is over $5. " if total > CONFIRM_ABOVE else ""
    if input(f"{msg}Proceed and call the paid API? [y/N] ").strip().lower() != "y":
        sys.exit("Cancelled, nothing was generated.")


# ---------------------------------------------------------------- API call
def generate(client, types, model, images, prompt, size, seed, retries=5):
    """One request -> (image bytes or None, response, model used). Retries 429/5xx and empty answers with backoff."""
    from google.genai import errors
    contents = []
    for i, (label, path) in enumerate(images, 1):
        contents.append(f"Image {i} ({label}):")
        contents.append(image_part(path, i == 1, types))
    contents.append(prompt)
    cfg = types.GenerateContentConfig(
        response_modalities=["IMAGE"], seed=seed,
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size=size))
    delay = 8
    for attempt in range(1, retries + 1):
        try:
            resp = client.models.generate_content(model=model, contents=contents, config=cfg)
            for cand in resp.candidates or []:
                for part in (cand.content.parts if cand.content else []) or []:
                    if part.inline_data and part.inline_data.data:
                        return part.inline_data.data, resp, model
            reason = resp.candidates[0].finish_reason if resp.candidates else getattr(resp, "prompt_feedback", None)
            print(f"   no image in the answer (reason: {reason}); attempt {attempt}/{retries}")
            if attempt >= 2:
                return None, resp, model
        except errors.ClientError as e:
            if e.code == 404 and model == MODEL:
                print(f"   model '{MODEL}' not found, switching to '{MODEL_FALLBACK}'")
                model = MODEL_FALLBACK
                continue
            if e.code != 429:
                raise
            print(f"   rate limited (429); waiting {delay}s, attempt {attempt}/{retries}")
        except errors.ServerError as e:
            print(f"   server error {e.code}; waiting {delay}s, attempt {attempt}/{retries}")
        time.sleep(delay)
        delay = min(delay * 2, 120)
    raise SystemExit("Giving up after repeated errors (see messages above). Nothing was billed for failed calls.")


def usage(resp):
    u = getattr(resp, "usage_metadata", None)
    g = lambda k: getattr(u, k, None) or 0 if u else 0
    return g("prompt_token_count"), g("candidates_token_count"), g("thoughts_token_count")


def save_png(data, path):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG")
    return im.size


def to_site_jpgs(src_img, view):
    """Return the image to save. The model's "16:9" is 2752×1536 (1.792). Measured on the front tests, it fits the
    whole camera frame into that canvas (tower edges matched best with a plain resize, not a crop), so the site
    version is a straight resize to 1920×1080 and the floor overlays line up."""
    MEDIA.mkdir(exist_ok=True)
    return src_img.convert("RGB")


# ---------------------------------------------------------------- composition check
COMPOSITION_MIN = 0.6   # good variants scored 0.73–0.96 in the Nov 2026 tests; one that ignored Image 1 scored 0.39


def composition_score(frame_path, img):
    """Correlation of blurred edge maps (3D frame vs generated image), 1.0 = identical layout."""
    from PIL import ImageFilter
    import math

    def emap(im):
        im = (Image.open(im) if not isinstance(im, Image.Image) else im).convert("L").resize((480, 270), Image.LANCZOS)
        return im.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(3)).tobytes()
    a, b = emap(frame_path), emap(img)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) or 1
    return num / den


# ---------------------------------------------------------------- contact sheet
def contact_sheet(view, files=None):
    """Camera frame + the given candidates (default: every candidate of the view)."""
    if files is None:
        files = sorted(CAND.glob(f"{view}_*.png"), key=lambda p: int(p.stem.rsplit("_", 1)[1]) if p.stem.rsplit("_", 1)[1].isdigit() else 0)
    if not files:
        print(f"No candidates for {view} yet.")
        return None
    tiles = [("3D camera frame (Image 1)", camera_frame(view))] + [(f.stem, f) for f in files]
    tw, th, pad, lab = 960, 540, 12, 34
    cols = 2
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * (th + lab) + (rows + 1) * pad), (18, 20, 24))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for i, (name, p) in enumerate(tiles):
        x = pad + (i % cols) * (tw + pad)
        y = pad + (i // cols) * (th + lab + pad)
        im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (x, y + lab))
        if i:
            sc = composition_score(camera_frame(view), p)
            name += f"   composition {sc:.2f}" + ("" if sc >= COMPOSITION_MIN else "  ✗ IGNORED IMAGE 1")
        d.text((x + 4, y + 6), name, fill=(226, 195, 143) if not i or sc >= COMPOSITION_MIN else (255, 90, 80), font=font)
    out = CAND / f"{view}_sheet.jpg"
    sheet.save(out, quality=88)
    print(f"Contact sheet: {out}")
    return out


# ---------------------------------------------------------------- main
def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")   # Windows consoles default to cp1252 (Málaga, ·, –)
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("views", nargs="*", help="front side back rooftop aerial, or all")
    ap.add_argument("--variants", type=int, default=3)
    ap.add_argument("--max-refs", type=int, default=DEFAULT_MAX_REFS,
                    help="send up to N reference photos after the camera frame (default 0: frame only, see DEFAULT_MAX_REFS)")
    ap.add_argument("--consistency", action="store_true",
                    help="add the approved media/front.jpg as the last image (off by default: extra images break the composition)")
    ap.add_argument("--refs", help="comma-separated reference name prefixes, overrides the per-view list")
    ap.add_argument("--max-total", type=float, help="refuse to run if the logged spend + this run would exceed this (USD)")
    ap.add_argument("--final", metavar="VIEW_N", help="re-run candidate VIEW_N at 4K -> media/<view>.jpg + <view>_4k.jpg")
    ap.add_argument("--promote", metavar="VIEW_N", help="use 2K candidate VIEW_N as media/<view>.jpg (no API call)")
    ap.add_argument("--sheet", metavar="VIEW", help="rebuild the contact sheet of VIEW only")
    ap.add_argument("--dry-run", action="store_true", help="print images, prompt and cost; no API call")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation for runs up to $5")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--list-models", action="store_true")
    a = ap.parse_args()

    if a.sheet:
        contact_sheet(a.sheet); return
    if a.promote:
        view = a.promote.rsplit("_", 1)[0]
        src = CAND / f"{a.promote}.png"
        if not src.exists():
            sys.exit(f"Not found: {src}")
        im = to_site_jpgs(Image.open(src), view)
        im.resize((1920, 1080), Image.LANCZOS).save(MEDIA / f"{view}.jpg", quality=92)
        print(f"media/{view}.jpg written from {src.name} (1920×1080). No API call.")
        return

    if a.list_models:
        from google import genai
        client = genai.Client(api_key=load_key())
        for m in client.models.list():
            if "image" in m.name.lower():
                print(m.name, "|", getattr(m, "display_name", ""))
        return

    # build the job list: (view, size, seed, out-name, images, prompt)
    jobs = []
    if a.final:
        meta_p = CAND / f"{a.final}.json"
        if not meta_p.exists():
            sys.exit(f"No metadata for {a.final} ({meta_p}). Pick a name from media/candidates/.")
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        images = [(lab, Path(p) if Path(p).is_absolute() else ROOT / p) for lab, p in meta["images"]]
        missing = [str(p) for _, p in images if not p.exists()]
        if missing:
            sys.exit("Input images changed or missing since the candidate was made: " + ", ".join(missing))
        jobs.append(dict(view=meta["view"], size="4K", seed=meta["seed"], name=f"{a.final}_4k", images=images,
                         prompt=meta["prompt"], final=True))
    else:
        views = VIEWS if (not a.views or a.views == ["all"]) else a.views
        bad = [v for v in views if v not in VIEWS]
        if bad:
            sys.exit(f"Unknown view(s): {bad}. Use {VIEWS} or all.")
        for v in views:
            images, prompt, warn = build_request(v, a.max_refs, a.refs.split(",") if a.refs else None, a.consistency)
            for w in warn:
                print(f"[{v}] WARNING: {w}")
            start = next_index(v)
            for k in range(a.variants):
                jobs.append(dict(view=v, size="2K", seed=random.randint(1, 2**31 - 1), name=f"{v}_{start + k}",
                                 images=images, prompt=prompt, final=False))

    total = sum(PRICE[j["size"]] + PRICE_INPUT_IMAGE * len(j["images"]) for j in jobs)
    shown = set()
    for j in jobs:
        if j["view"] in shown:
            continue
        shown.add(j["view"])
        n_out = sum(1 for x in jobs if x["view"] == j["view"])
        print(f"\n=== {j['view']} · {n_out} output image(s) at {j['size']} · {len(j['images'])} input images ===")
        for i, (lab, p) in enumerate(j["images"], 1):
            print(f"  Image {i:2d}: {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}   [{lab}]")
        if a.dry_run:
            print("\n--- prompt ---\n" + j["prompt"] + "\n--------------")
    print(f"\n{len(jobs)} output image(s) at {', '.join(sorted({j['size'] for j in jobs}))}: ${total:.2f} estimated "
          f"(${PRICE['2K']}/2K, ${PRICE['4K']}/4K, inputs ~${PRICE_INPUT_IMAGE}/image)")
    if a.dry_run:
        print("Dry run: no API call, nothing billed.")
        return
    if a.max_total is not None and spent_so_far() + total > a.max_total:
        sys.exit(f"Budget cap: logged ${spent_so_far():.2f} + this run ${total:.2f} would exceed --max-total ${a.max_total:.2f}.")
    confirm(total, a.yes)

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=load_key())
    model = a.model
    run_cost, done = 0.0, {}
    for j in jobs:
        sha = hashlib.sha1(j["prompt"].encode()).hexdigest()[:10]
        print(f"\n-> {j['name']}  ({j['size']}, seed {j['seed']})")
        t0 = time.time()
        data, resp, model = generate(client, types, model, j["images"], j["prompt"], j["size"], j["seed"])
        pt, ot, tt = usage(resp)
        imgs = ";".join(str(p.name) for _, p in j["images"])
        if data is None:
            log_row(time=datetime.datetime.now().isoformat(timespec="seconds"), view=j["view"], file="", size=j["size"],
                    model=model, seed=j["seed"], prompt_sha=sha, images=imgs, status="no_image", cost_usd=0,
                    prompt_tokens=pt, output_tokens=ot, thought_tokens=tt, note="no image returned")
            print("   no image returned (logged); continuing")
            continue
        cost = PRICE[j["size"]] + PRICE_INPUT_IMAGE * len(j["images"])
        run_cost += cost
        if j["final"]:
            im = Image.open(io.BytesIO(data))
            out_w, out_h = im.size
            if composition_score(camera_frame(j["view"]), im) < COMPOSITION_MIN:
                rej = CAND / f"{j['name']}_rejected.png"
                im.convert("RGB").save(rej)
                log_row(time=datetime.datetime.now().isoformat(timespec="seconds"), view=j["view"], file=rej.name,
                        size=j["size"], model=model, seed=j["seed"], prompt_sha=sha, images=imgs, status="ok",
                        cost_usd=f"{cost:.4f}", prompt_tokens=pt, output_tokens=ot, thought_tokens=tt, out_w=out_w,
                        out_h=out_h, note="4K re-run ignored Image 1; media/ not touched")
                print(f"   the 4K re-run ignored Image 1 (saved as {rej.name}); media/{j['view']}.jpg NOT changed. "
                      f"Use --promote {j['name'][:-3]} instead.")
                continue
            im = to_site_jpgs(im, j["view"])
            im.save(MEDIA / f"{j['view']}_4k.jpg", quality=93)
            im.resize((1920, 1080), Image.LANCZOS).save(MEDIA / f"{j['view']}.jpg", quality=92)
            out = MEDIA / f"{j['view']}.jpg"
            print(f"   saved media/{j['view']}_4k.jpg ({out_w}×{out_h}) and media/{j['view']}.jpg (1920×1080)")
        else:
            out = CAND / f"{j['name']}.png"
            out_w, out_h = save_png(data, out)
            (CAND / f"{j['name']}.json").write_text(json.dumps(dict(
                view=j["view"], seed=j["seed"], model=model, prompt=j["prompt"],
                images=[(lab, p.relative_to(ROOT).as_posix()) for lab, p in j["images"]]), indent=1,
                ensure_ascii=False), encoding="utf-8")   # project-relative paths: no local user paths in the repo
            print(f"   saved {out.relative_to(ROOT)} ({out_w}×{out_h}) in {time.time()-t0:.0f}s")
        if out_w < (1800 if j["size"] == "2K" else 3600):
            print(f"   NOTE: output is only {out_w}×{out_h}; the requested size may have been ignored.")
        sc = composition_score(camera_frame(j["view"]), out)
        verdict = "OK" if sc >= COMPOSITION_MIN else "LOW: the model probably ignored Image 1, reject"
        print(f"   composition score {sc:.2f} ({verdict})")
        log_row(time=datetime.datetime.now().isoformat(timespec="seconds"), view=j["view"], file=out.name,
                size=j["size"], model=model, seed=j["seed"], prompt_sha=sha, images=imgs, status="ok",
                cost_usd=f"{cost:.4f}", prompt_tokens=pt, output_tokens=ot, thought_tokens=tt, out_w=out_w, out_h=out_h,
                note=f"composition {sc:.2f}")
        done.setdefault(j["view"], []).append(out)
        print(f"   running total this run: ${run_cost:.2f}")

    for v, files in done.items():
        if not a.final:
            contact_sheet(v, files)        # this run's variants next to the camera frame (--sheet <view> = all of them)
    print(f"\nRun cost ≈ ${run_cost:.2f}. Logged total: ${spent_so_far():.2f}. Log: {LOG.relative_to(ROOT)}")
    print("\nQA before keeping a still (reject if any fail):")
    for q in QA:
        print("  [ ] " + q)
    if not a.final:
        print("\nPick the best, then:  python gen_stills.py --final <view>_<n>   (4K, ~$0.24)"
              "\n                  or:  python gen_stills.py --promote <view>_<n> (use the 2K as is, free)")


if __name__ == "__main__":
    main()
