# Málaga Towers: Higgsfield pipeline

The 3D model in `index.html` is the camera rig. Every Higgsfield shot is locked to one of its frames, so the clickable floors in the 3D line up exactly with the AI photos.

```
index.html  →  exports/still-*.png (camera lock)  →  Nano Banana Pro (photoreal stills)
            →  Kling 3.0 start/end frame (5 s clips)  →  media/  →  index.html plays them
```

## Cost (checked Nov 2026; Higgsfield changes this often, so recheck the pricing page)

| Item | Credits each | How many (incl. retries) | Credits |
|---|---|---|---|
| Nano Banana Pro still, 2K | 2 | 5 views × ~6 tries | ~60 |
| Final stills in 4K | 4 | 5 | 20 |
| Kling 3.0 clip, 5 s | ~7–10 (720p) / ~10–13 (1080p) | 5 clips × ~5 tries | ~200–320 |
| **Total** | | | **~300–400** |

- **Plus plan (~$49–59/month, 1,000–1,200 credits)** covers it with plenty left over for retries. On the annual Plus plan, Kling 3.0 is unlimited during the 7-day windows, so if you time the clips inside one, they cost no credits.
- Starter (~$15–19, 200–270 credits) is too tight for the clips.
- You only need **one month**: about **$50–60**. Cancel after.
- Reversed clips are free (ffmpeg, step 4).

## Step 0: Reference photos
Double-click **GET-REFS.bat**. It downloads 21 full-resolution photos and renders into `refs/full/`. Smaller previews are already in `refs/preview/`.
These are the architect's and press photos. Use them only as private AI reference, and **don't put them on the website.** The 3 Wikimedia photos (11–13) are CC BY-SA 4.0.

Best references by job:
- **Facade (white plates, glass, balustrades):** 02, 03, 12, 20
- **Whole towers from the beach/promenade:** 13, 19, 15, 01
- **Aerial / context:** 14, 01, 21, 22
- **Rooftop pool:** 07, 08, 09

## Step 1: Camera frames
Use the `*-sunset.png` files in `exports/` (1920×1080). Ignore the old day and clouds files.
If you change a view: open `index.html?dev`, orbit to your view, click **Copy current camera**, and paste the result into `VIEWS` in the code. Then **① Export 5 stills**.
For motion references, click **② Record 5 flight clips**. It records in real time, so keep the tab in front.

## Step 2: Stills in Nano Banana Pro (16:9, 2K, then 4K for the keeper)
Upload: **Image 1 = the export still** for that view, **Images 2–4 = the refs listed below**.

**Master prompt (paste every time, then add the view line and the light line):**
> Image 1 is the exact frame of this photograph. Keep the camera position, height, lens, framing and the outline, height and position of every building exactly as in Image 1; only surfaces, light and realism change. Images 2–4 are real photographs of the same towers: use them for the white slab plates, the glass, the balustrades, the louvres, the planting and the street; their cameras are ignored. Málaga Towers by Estudio Lamela: three identical 21-storey residential towers in a row on the Paseo Marítimo Antonio Banderas, Misericordia beach, Málaga. Every floor is ringed by thick bright-white cantilevered slab plates about one metre deep in section; their projection changes from floor to floor and from segment to segment, so each tower's outline is a jagged stack of white bands with deep shadow beneath every plate. Frameless clear glass balustrades on every plate; recessed dark grey-blue floor-to-ceiling glazing with slim dark frames; grey horizontal-slat louvre panels in a few bays; white angled vertical fins over a glazed double-height lobby; rooftop infinity pool and timber-clad plant room. Landscaped plaza with terracotta pergolas, lawns and shallow water features; a wide palm-lined road and promenade with a red cycle lane; a wide golden sand beach and the Mediterranean. Photoreal architectural photograph, natural colour, crisp detail, no people in focus, 16:9.

**View lines:**
| View | Add this | Refs (Images 2–4) |
|---|---|---|
| front | Seen from just above the sea, looking inland across the beach, promenade and road at the three towers, mountains of the Montes de Málaga behind the city. | 13, 01, 02 |
| side | Seen from the promenade to the east, looking west along the coast: rows of palms, the road and the beach leading to the three towers. | 19, 15, 16 |
| back | Drone view from the city side at mid height, looking over the plaza and the three towers to the beach and open sea beyond. | 14, 01, 11 |
| rooftop | From just above the rooftop of the eastern tower: infinity pool and timber plant room in the foreground, the other two towers and the coastline beyond. | 07, 08, 06 |
| aerial | High drone view from above the sea to the south-west, looking north-east along the coast: the three towers in a row beside the palm-lined road and promenade, the beach and sea on the right, the city, the brick chimney and the mountains beyond. | 14, 01, 21 |

**Light line (use for every shot, sunset is the look):**
- Sunset: *A few minutes before sunset, low warm sun from the west raking across the left faces, white plates glowing apricot, shaded faces cool blue, soft haze over the sea.*

If the plates come out flat or regular, re-run with: *the plates are irregular and staggered, never aligned floor to floor*.

## Step 3: Clips in Kling 3.0 (start + end frame, 5 s)
Start image = still A, end image = still B (always going forward in this order: front → side → back → rooftop → aerial → front).
If Higgsfield offers motion/video reference, also attach the matching `clip-A-B.webm` from step 1.

> Real drone footage. The video starts exactly on the start image and ends exactly on the end image. The three white towers, their staggered white plates, glass, palms, beach and sea stay exactly as in the images; no new buildings, no morphing, no warping. Smooth stable camera at real speed. MOTION

| Clip | MOTION |
|---|---|
| front → side | The drone rises slightly and arcs to the right around the towers to a low view along the promenade from the east. |
| side → back | The drone climbs and swings round behind the towers to a high view from the city side with the sea beyond. |
| back → rooftop | The drone descends towards the eastern tower and settles just above its rooftop pool. |
| rooftop → aerial | The drone lifts off the rooftop, climbs and pulls back out over the sea to a high view along the coast. |
| aerial → front | The drone descends over the sea and glides in low, facing the towers across the beach. |

## Step 4: Name, reverse and compress
Save the 5 clips as `media/front-side.mp4`, `media/side-back.mp4`, `media/back-rooftop.mp4`, `media/rooftop-aerial.mp4`, `media/aerial-front.mp4`, then in that folder:
```bash
for %f in (front-side side-back back-rooftop rooftop-aerial aerial-front) do ffmpeg -y -i %f.mp4 -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart %f-web.mp4
ffmpeg -y -i front-side-web.mp4 -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart side-front.mp4
ffmpeg -y -i side-back-web.mp4 -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart back-side.mp4
ffmpeg -y -i back-rooftop-web.mp4 -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart rooftop-back.mp4
ffmpeg -y -i rooftop-aerial-web.mp4 -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart aerial-rooftop.mp4
ffmpeg -y -i aerial-front-web.mp4 -vf reverse -an -c:v libx264 -crf 20 -preset veryfast -movflags +faststart front-aerial.mp4
```
Save the final stills as `media/front.jpg`, `side.jpg`, `back.jpg`, `rooftop.jpg`, `aerial.jpg` (1920×1080, JPG quality ~85).

## Step 5: Plug in
In `index.html`, fill `CONFIG.media`:
```js
media: {
  stills: { front:'media/front.jpg', side:'media/side.jpg', back:'media/back.jpg', rooftop:'media/rooftop.jpg', aerial:'media/aerial.jpg' },
  clips: {
    'front>side':'media/front-side-web.mp4',      'side>front':'media/side-front.mp4',
    'side>back':'media/side-back-web.mp4',        'back>side':'media/back-side.mp4',
    'back>rooftop':'media/back-rooftop-web.mp4',  'rooftop>back':'media/rooftop-back.mp4',
    'rooftop>aerial':'media/rooftop-aerial-web.mp4','aerial>rooftop':'media/aerial-rooftop.mp4',
    'aerial>front':'media/aerial-front-web.mp4',  'front>aerial':'media/front-aerial.mp4',
  },
},
```
Run it with a local server so video loads reliably: `npx serve` in this folder, then open the printed URL.
Once a still loads, the page shows the photo; hovering or clicking floors still works through the hidden 3D. Switching views plays the clips the shortest way round. Dragging the photo drops back into the live 3D.
