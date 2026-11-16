# Málaga Towers: making it photoreal (gen_stills.py + Kling)

The 3D in `index.html` is the camera rig. Every AI shot is locked to one of its frames, so the clickable floors line up exactly with the photos.

```
exports/still-*-sunset.png ─► gen_stills.py (Nano Banana Pro API) ─► media/front.jpg … (5 stills)
5 stills ─────────────────► Kling 3.0 start+end frame ──────────► media/front-side.mp4 … (5 clips + reversed)
each still ───────────────► Kling 3.0 same start+end frame ─────► media/front-loop.mp4 … (idle loops)
```

**Cost:** stills ≈ $0.40 per view for 3 variants plus $0.24 per 4K final (≈ $3.20 for all 5 views; the first full set incl. all tests cost $4.49). Video is Kling Standard, about $7 for the first month (660 credits). **Cancel before it renews.**

---

## 0. Prep (5 min)
1. Double-click **GET-REFS.bat**. The full-res reference photos land in `refs/full/`.
2. The camera frames are already in `exports/` (`still-<view>-sunset.png`, re-exported 16 Nov 2026 after the model fix). Ignore the old `*-day.png` and `*clouds*` files.
3. Make a `media/` folder. It's already there.

---

## 1. Stills: run the script (Nano Banana Pro via the Gemini API)
The script `gen_stills.py` does everything that used to be manual in AI Studio. It sends **only the 3D camera frame** with a prompt that tells the model to turn that frame into a photo without moving the camera. Tests showed that adding reference photos (even one taken from the same angle) makes the model ignore the frame, so references are off by default. It saves the variants, scores each one against the frame, logs every request and builds a contact sheet.

**The five stills are done** (16 Nov 2026): `media/front.jpg`, `side.jpg`, `back.jpg`, `rooftop.jpg`, `aerial.jpg` (+ `_4k.jpg`), already plugged into `index.html`. Use the steps below only to redo a view, for example after changing the 3D model.

**Cost:** $0.134 per 2K image, $0.24 per 4K image (input images ≈ $0.001 each). Every paid run shows its cost and asks before calling the API.

1. **API key:** the script reads `GEMINI_API_KEY` (already set on Martin's PC), otherwise it asks once and saves it to `.env` (ignored by git). Never paste the key into the code.
2. **Check first (free):** double-click **GEN-STILLS.bat** and type `front --dry-run`. It prints the image it would send and the full prompt.
3. **Front first:** run `front`. That's 3 variants at 2K (~$0.40) in `media/candidates/front_1.png …`, plus `front_sheet.jpg` showing the 3D frame next to every variant. Each variant gets a **composition score** (printed and on the sheet). Below 0.6 means the model ignored the frame (it happens about 1 time in 6), so reject it.
4. **Check each variant** against the QA list below and pick the best, e.g. `front_2`.
5. **Finalise:** `--final front_2` re-runs it at 4K (~$0.24) and writes `media/front.jpg` (1920×1080 for the site) and `media/front_4k.jpg`. If the 4K re-run comes out worse, `--promote front_2` uses the 2K candidate as `media/front.jpg` for free.
6. **Other views:** run `side`, `back`, `rooftop`, `aerial` (or `all`) with the same prompt, so the light matches, then finalise each one as in step 5. `--consistency` adds the approved front as an extra image, but that can break the composition, so test with 1 variant first.

Useful options: `--variants 4`, `--yes` (skip the confirmation for runs up to $5), `--max-total 10` (refuse to go over a total budget), `--sheet front` (rebuild a contact sheet with every candidate), `--list-models` (free), `--max-refs N` / `--refs a,b` (experiments with reference photos). Every request goes into `media/candidates/log.csv` (view, seed, images, prompt hash, cost, tokens, output size).

**Quality check before keeping a still (reject if any fail):**
- Composition matches Image 1. Flick between the variant and the 3D frame: the towers must sit in the same pixels.
- Each tower has **21 floors + base**, and the base looks like the real one: recessed dark ground floor, a white band with straight posts.
- The plates are **irregular and staggered**, not neat rings.
- No palms on open sand, the beach bar is there, and the warehouses are next to the towers.
- No logos, no text except "92", no invented extra towers.
- Sunset light consistent with the approved front.

---

## 2. Video in Kling (≈ $7)
1. Go to **klingai.com**, sign in, and buy **Standard**. Don't use the free plan: it adds a watermark and doesn't allow commercial use.
2. Open **Video → Image to Video**. Pick the newest model (**Kling 3.0**), set duration **5 s**, and use **Start frame + End frame**.
3. Check the credit cost shown before you press Generate. 660 credits ≈ 22 clips at 720p, fewer at 1080p.
4. Negative prompt (if there's a field): *warping, morphing, melting, extra buildings, extra floors, text, watermark, flicker, people close-up.*

### 2a. Transition clips (5 clips, ~450 credits with retries)
Start = still A, end = still B. Always go forward: **front → side → back → rooftop → aerial → front**.

> Real drone footage. The video starts exactly on the start image and ends exactly on the end image. The three white towers, their staggered white plates, glass, palms, beach and sea stay exactly as in the images; no new buildings, no morphing, no warping. Smooth stable camera at real speed, golden sunset light throughout. MOTION

| Save as | MOTION |
|---|---|
| `front-side.mp4` | The drone rises slightly and arcs to the right around the towers to a low view along the promenade from the east. |
| `side-back.mp4` | The drone climbs and swings round behind the towers to a high view from the city side with the sea beyond. |
| `back-rooftop.mp4` | The drone descends towards the eastern tower and settles just above its rooftop pool. |
| `rooftop-aerial.mp4` | The drone lifts off the rooftop, climbs and pulls back out over the sea to a high view along the coast. |
| `aerial-front.mp4` | The drone descends over the sea and glides in low, facing the towers across the beach. |

### 2b. Idle loops (5 clips, ~150 credits, only if credits are left)
Use the **same still as both start and end frame**. The clip then loops seamlessly.
> Locked-off tripod shot, the camera does not move at all. Only gentle natural motion: small waves rolling onto the beach, palm fronds swaying in a light breeze, a few cars moving on the road, tiny distant pedestrians on the promenade, a few apartment lights switching on as the sun sets. Buildings stay perfectly still and unchanged.

Save as `front-loop.mp4`, `side-loop.mp4`, `back-loop.mp4`, `rooftop-loop.mp4`, `aerial-loop.mp4`.

If you're out of credits, skip the loops. The site works with the still photos alone.

---

## 3. Reverse + compress (free, ffmpeg)
In the `media` folder (Windows cmd):
```bat
for %f in (front-side side-back back-rooftop rooftop-aerial aerial-front) do ffmpeg -y -i %f.mp4 -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart %f-web.mp4
ffmpeg -y -i front-side-web.mp4     -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart side-front.mp4
ffmpeg -y -i side-back-web.mp4      -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart back-side.mp4
ffmpeg -y -i back-rooftop-web.mp4   -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart rooftop-back.mp4
ffmpeg -y -i rooftop-aerial-web.mp4 -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart aerial-rooftop.mp4
ffmpeg -y -i aerial-front-web.mp4   -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart front-aerial.mp4
for %f in (front side back rooftop aerial) do ffmpeg -y -i %f-loop.mp4 -an -c:v libx264 -crf 22 -preset veryfast -movflags +faststart %f-loop-web.mp4
```
(No ffmpeg? Run `winget install ffmpeg`, then reopen cmd.)

---

## 4. Plug in
In `index.html`, replace the `media:` block in `CONFIG` with:
```js
media: {
  stills: { front:'media/front.jpg', side:'media/side.jpg', back:'media/back.jpg', rooftop:'media/rooftop.jpg', aerial:'media/aerial.jpg' },
  clips: {
    'front>side':'media/front-side-web.mp4',        'side>front':'media/side-front.mp4',
    'side>back':'media/side-back-web.mp4',          'back>side':'media/back-side.mp4',
    'back>rooftop':'media/back-rooftop-web.mp4',    'rooftop>back':'media/rooftop-back.mp4',
    'rooftop>aerial':'media/rooftop-aerial-web.mp4','aerial>rooftop':'media/aerial-rooftop.mp4',
    'aerial>front':'media/aerial-front-web.mp4',    'front>aerial':'media/front-aerial.mp4',
  },
  loops: { front:'media/front-loop-web.mp4', side:'media/side-loop-web.mp4', back:'media/back-loop-web.mp4', rooftop:'media/rooftop-loop-web.mp4', aerial:'media/aerial-loop-web.mp4' },
},
```
Leave out any file you don't have (set it to `null`), and the page falls back gracefully.

Run it: open cmd in the project folder, type `npx serve`, and open the URL it prints.
What you get: each view shows its photo (or loop), clicking floors works on top of it, switching views plays the drone clips, and dragging drops into the live 3D.

---

## Rules for the reference photos
The photos in `refs/` are the architect's and press photos. Use them only as private AI references, **never on the website.** Only 11–13 (Wikimedia) are freely licensed (CC BY-SA 4.0).
