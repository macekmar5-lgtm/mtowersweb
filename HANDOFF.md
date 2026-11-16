# Málaga Towers: Handoff

> Status 16 Nov 2026. This document holds everything needed to continue: the goal, what exists, the decisions made, what's wrong, and exactly what to build next.
> **Your two jobs:** (1) fix the 3D model thoroughly against the real references, then (2) build the API script that generates the photoreal stills.

---

## 1. Goal

An interactive sales website for **Málaga Towers** (Estudio Lamela / Metrovacesa + Sierra Blanca, Paseo Marítimo Antonio Banderas, Misericordia beach, Málaga). It has two layers:

1. **Photoreal layer.** AI-generated stills (Google Nano Banana Pro) and drone-flight clips (Kling 3.0). Visitors see these.
2. **Invisible 3D layer.** A three.js model of the real towers, rendered from exactly the same cameras. It handles hover/click on floors, highlights, unit plans and filters.

The trick is that every AI still is generated **from a frame exported from the 3D model** (camera lock). The 3D geometry therefore lines up with the photo pixel for pixel, and clicking a floor on the photo hits the right floor in 3D.

**Quality bar:** it has to be "as realistic as possible". Wrong surroundings, wrong palms or a wrong tower base are not acceptable. The client-side owner (Martin) checks against reality.

**Status of the work:** this is a concept or pitch. All unit prices and availability are **sample data**, and the page is labelled "Concept · sample data". Keep it that way until real data exists.

---

## 2. Decisions already made (don't revisit)

| Topic | Decision |
|---|---|
| Lighting | **Sunset only** ("a few minutes before sunset", warm low sun from the west). The day mode stays in the 3D as a toggle but isn't used for renders. |
| Views | **5 views:** `front`, `side`, `back`, `rooftop`, `aerial`. **"Above the clouds" was dropped.** |
| Stills | **Google Gemini API, model `gemini-3-pro-image` (Nano Banana Pro)**, billing enabled, $0.134 per output image. Via a script, not the AI Studio UI. |
| Video | **Kling Standard (~$7 a month)** on klingai.com, start + end frame, 5 s, Kling 3.0. Not Higgsfield (same models, about 8× the price). Done manually later. |
| Idle loops | Optional: Kling with the same still as start and end frame. The page already supports loops. |
| Mobile | Not required. Desktop only. |
| Reference images | Max **14 images per request** (Google limit: "Maximum images per prompt: 14"). Each input image costs 560 tokens, which is negligible. |

---

## 3. Project folder

`C:\Users\Martin\Desktop\PROJEKTY\Malaga towers\`

```
index.html               ← the whole app (three.js, UI, photo mode, dev export). Single file, CDN imports.
index-v1-old.html        ← first prototype (fictional towers). Ignore.
GUIDE.md                 ← end-user steps for AI Studio / Kling / ffmpeg / plug-in (will need updating once the script exists)
HANDOFF.md               ← this file
HIGGSFIELD-GUIDE.md      ← obsolete stub
GET-REFS.bat / get-refs.ps1  ← downloads refs/full (already done, 21/21 OK)
exports/                 ← 3D camera frames 1920×1080 (still-<view>-sunset.png). Regenerate after fixing the model!
                           (old *-day.png and *clouds* files are obsolete)
media/                   ← final AI stills/clips go here. Contains README.txt and aerial_candidate_01.jpg (see §7)
refs/full/               ← 21 full-res photos from the architect, press and Wikimedia
refs/preview/            ← same 21 small, plus 22_satellite_site.jpg (old satellite, construction phase)
refs/video/              ← 32 frames from YouTube videos (BEST references, see §4)
refs/user/               ← Martin's own screenshots (sv_01_tower_base_street.png = the real tower base)
```

Run locally with `npx serve` in the folder (video needs a server). Dev tools: `index.html?dev`.

---

## 4. Reference inventory (what each file is good for)

### refs/video/ (from YouTube, the most important)
`v3_*` frames come from a 4K drone marketing video (NVOGA logo cropped off). `v1_*` frames come from an apartment tour video (1080p).

| File | Shows | Use for |
|---|---|---|
| **v3_4k_front_from_sea_golden_hour.jpg** | All 3 towers head-on from the sea at golden hour | **THE target look for `front`** |
| v3_4k_front_from_sea_day / _blue_hour / _night | Same angle, other light | front: geometry, spacing, neighbours |
| v3_4k_front_from_beach_1/2 | From above the beach/road, all 3 towers, beach bars, road, palms | front, side: street layout |
| v3_4k_drone_oblique_beach_road_1/2 | Oblique drone over beach and road, warehouses on the right | aerial, side |
| v3_4k_drone_between_towers_sea | Drone between the towers looking at the sea | back, plate detail |
| v3_4k_entrance_92_dusk | Entrance canopy with angled white fins and the "92" sign | tower base |
| v3_4k_podium_pool_garden | Communal pool / podium garden | back, plaza |
| v3_4k_rooftop_pool_coast / _2 | Rooftop infinity pool, dark plant room, coast | rooftop |
| v3_4k_sunset_coast_chimney_port | Sunset over the coast, Los Guindos chimney, port cranes | sunset colour, context |
| v3_4k_view_beach_from_tower | Beach seen from a tower | beach layout |
| v1_drone_from_sea_warehouses | **Real drone from the sea: warehouses (blue-grey roofs) next to and behind the towers** | front, aerial context |
| v1_drone_from_sea_low_beach | Low drone over the beach toward the towers | front |
| v1_drone_oblique_promenade | Oblique over the promenade, roundabout | side, aerial |
| v1_drone_tower_closeup_sea | One tower close, sea behind | plates |
| v1_view_promenade_beach_from_tower, v1_view_beach_breakwater_2, v1_terrace_view_beach_breakwater, v1_view_coast_roundabout | Looking down on the promenade, beach, breakwater and road | **real palm placement, promenade paving, beach** |
| v1_terrace_neighbour_tower, v1_terrace_city_side_1/2 | The neighbouring tower; city side with low residential blocks | back, plates |
| v1_terrace_sea_view | Terrace furniture and sea | rooftop or terrace mood |
| v1_render_* (5) | Developer marketing renders (gardens, pond, promenade, rooftop pool, 3 towers from the city) | plaza design, back |

### refs/full/ (architect, press, Wikimedia)
01 hero render · 02/03/04/20 plate details (best facade detail) · 05 entrance fins · 06 terrace sea view · 07–09 rooftop pool · 10 lobby · 11–13 Wikimedia photos (two towers, facade up, from beach) · 14 idealista aerial render · 15/16 street photos · 17 chimney and towers · 18 towers in fog · 19 promenade (aluman) · 21 competition render.

### refs/user/
`sv_01_tower_base_street.png` is Martin's Street View screenshot of the real base. **Ground truth for the base.**

**Copyright:** refs are architect, press and marketing images. Use them only as private AI references, never on the website. Only 11–13 are CC BY-SA.

**Not usable:** Google Maps satellite/3D and Street View mostly show the construction phase (outdated). The YouTube frames are newer.

---

## 5. Facts about the real towers and site (verified from the refs)

### Towers
- 3 identical towers, **21 residential floors + ground floor**, in a row **parallel to the coast**, with even spacing and facades aligned (compare `v3_4k_front_from_sea_day`). 71 homes per tower, 45,680 m² total, completed 2025.
- Plot ~26×26 m per tower. The current model uses a **24×18 m glass core** with plates cantilevering up to ~4 m. **Re-check the proportions** against the front-from-sea frames: the towers look roughly as wide as they are deep, and the spacing between towers is about 1.3–1.6 × the tower width (measure it).
- **Facade:** every floor has a thick bright-white slab "plate" (~0.9–1 m edge) that cantilevers by a different amount per segment and per floor, giving a jagged, stacked outline. Frameless glass balustrades on every plate. Recessed dark grey-blue full-height glazing. Grey horizontal-slat louvre panels in some bays.
- **Top:** a flat roof with a dark/graphite plant room (some renders show timber cladding; the real one in `v3_4k_rooftop_pool_*` is dark grey), an infinity pool on the sea side and glass balustrades.

### Base (currently WRONG in the 3D, the AI copied it, and Martin flagged it)
From `refs/user/sv_01_tower_base_street.png` and `v3_4k_entrance_92_dusk.jpg`:
- **Ground floor:** dark glass, **recessed** under a deep white overhang, with the "92" entrance sign.
- **1st floor:** a **wide continuous white band**, with a row of **straight vertical white posts/fins** in the middle section (not angled fins all round).
- At the entrance there is a **canopy with angled white fins** (`v3_4k_entrance_92_dusk`). These are local to the entrance only.
- A **low white podium wing (1–2 floors)** connects at street level / extends sideways.
- The typical staggered plates start above that.

### Surroundings (currently WRONG or too generic)
- **Directly next to and behind the towers:** large **industrial warehouses with blue-grey sawtooth/flat roofs** (`v1_drone_from_sea_warehouses`, `v3_4k_drone_oblique_*`).
- **Between and around the towers:** **low white residential blocks** (4–8 floors) visible between the towers from the sea, plus the landscaped plaza with lawns, ponds, terracotta pergolas and the communal pool.
- **In front (toward the sea), in order:** plaza edge → **wide road (Calle Pacífico / Paseo Marítimo Antonio Banderas), ~6 lanes with a palm median** → **promenade with a red cycle lane and rows of palms** → **wide sandy beach (~70–90 m)** with **beach bars (chiringuitos)**, sunbeds, small clusters of palms/vegetation near the bars and lifeguard posts → the Mediterranean.
- **Palms:** along the road median and the promenade, plus clusters at the beach bars. **No neat rows of palms on the open sand**; Martin called that out as unrealistic.
- **To the east (toward the city centre):** a **stone breakwater** into the sea, the **Los Guindos brick chimney** (~100 m), and further on the **port with cranes**.
- **Behind (inland):** a dense city of mid-rise residential blocks, then the **Montes de Málaga** mountains.
- A roundabout near one end of the site (`v1_view_coast_roundabout`).

---

## 6. Current code: how index.html works

Single file, three.js 0.170 via importmap (jsdelivr). Key parts, in file order:

- **`CONFIG`**: `floors:21, floorH:3.3, groundH:6.2, slabT:0.95, W:24, D:18, coreW/coreD`, towers `{id,x,z,seed}` (A x=-82 z=-50 · B x=0 z=-60 · C x=82 z=-53), and `media:{stills, clips, loops}`.
- **Coordinates:** metres, **+x = along the coast toward the city centre / port (east-ish)**, **+z = toward the sea**, y up. Ground at y=0. Road z≈-10…18, promenade z≈18…44, beach z≈44…117, water beyond.
- **`ORDER` / `VIEWS`**: 5 cameras `{pos,target}`. The camera is **fov 34°, fixed 16:9**, cropped to the window like CSS `object-fit:cover` via `setViewOffset` (`fitCamera()`). **Exports and AI stills must stay 16:9 at 1920×1080.**
- **`makePlates(rand, level)`**: generates the staggered plates per floor (4 faces × 2 segments plus corner pieces, depths from `DEPTHS`) and the balustrade strips. Seeded, so it's deterministic.
- **`makeUnits(f)`**: sample sales data (floors 1–16: 4 units, 17–19: 2 units of 219 m², 20–21: duplex penthouse of 384 m²).
- Geometry is **InstancedMesh everywhere** (glass, plates, rails, louvres, fins, trees, palms, city). Shadows are **baked once** (`shadowMap.autoUpdate=false`). Keep it optimized; Martin's rule: "look good but optimized, no lag".
- **Site section** (search `/* ---------------- site`): water plane, land, plaza, road, promenade, cycle lane, beach, lawns, ponds, pergolas, palms, trees, generic city boxes, chimney, hills. **This is what needs the biggest rework.**
- **`setTime('day'|'sunset')`**: sky, sun, fog, env map (PMREM from Sky). Default is sunset.
- **Picking**: raycast against `glassMesh` and `plateMesh` → floor (`glassF` / `plateF` maps). If you add new solid geometry that should block clicks, add it to `blockers`.
- **Photo mode**: if `CONFIG.media.stills[view]` exists, the still is shown full-screen, the canvas goes invisible (opacity 0, still receives events), and hover/selection are drawn as **SVG hull polygons** projected from the 3D (`projRects`, `drawOverlay`). Loops (`media.loops`) play on top of the still. View changes play `media.clips['a>b']` along the shortest path through `ORDER`. Dragging exits to the live 3D.
- **Dev panel** (`?dev`): ① **Export 5 stills** (1920×1080 PNG, UI hidden, current time of day) → browser Downloads as `still-<view>-<tod>.png`; ② **Record 5 flight clips** (5 s WebM each, real-time, keep the tab focused); **Copy current camera** → JSON `{pos,target}` for `VIEWS`.
- `window.__towers` exposes `state, TOWERS, goView, selectFloor, selectUnit, renderer, setTime, flying()` for testing.

---

## 7. What happened so far with AI generation

- **First test** (AI Studio UI, Nano Banana Pro, front frame + 7 refs): the result was photoreal and good-looking, **but it ignored the camera lock** and copied the composition of ref `01_render_hero_lamela` (a low oblique drone shot). It's saved as `media/aerial_candidate_01.jpg`. Martin's verdict: **the palms at the beach were unrealistic, the surroundings didn't match, and the tower base was wrong.**
- **Lessons:**
  1. Image 1 (the camera frame) must contain the **correct surroundings**. The AI follows whatever the 3D shows, or invents things where the 3D is vague.
  2. **Never include references whose composition is similar to another view.** `01_render_hero_lamela` hijacked the front. For each view, prefer references that either match that view's angle or are close-up details.
  3. The prompt needs an explicit composition lock ("Image 1 is the ONLY source for composition… do not copy the camera of any other image").
- **Option:** `aerial_candidate_01.jpg` could become the `aerial` still if the 3D `aerial` camera is calibrated to match it. Its surroundings are wrong though, so regenerating after the model fix is better. Ask Martin.

---

## 8. JOB 1: Fix the 3D model (do this first)

The 3D frame is what the AI paints over, so **every error here shows up in the photos.** Work view by view, comparing your export side by side with the matching reference.

### 8.1 Tower base (high priority)
Rebuild ground + 1st floor per §5 "Base":
- [ ] Ground floor: dark glass box recessed ~2–3 m behind the 1st-floor edge, full footprint. "92" entrance on the street (north/road) side.
- [ ] 1st floor: wide white continuous band (solid, not staggered plates), with a row of straight vertical white posts in the central section.
- [ ] Entrance canopy with angled white fins, **only at the entrance** (remove the current angled fins all around: `finM` in the towers section).
- [ ] Low white podium wing (1–2 floors) linking at street level. Check the extent against `sv_01` and `v3_4k_front_from_beach_*`.
- [ ] Typical plates start from floor 2. Re-check the total height (21 floors + ground) against the photos. Currently `groundH 6.2 + 21×3.3`.

### 8.2 Tower proportions and placement
- [ ] Compare the export of `front` against `v3_4k_front_from_sea_day.jpg`: tower width vs height, spacing, alignment (the real towers sit in a straight row, evenly spaced; the current model staggers z by up to 10 m, so check it).
- [ ] Plate depth and thickness vs `02/03/20` and `v1_drone_tower_closeup_sea`. Real plates are deep (up to ~3–4 m) and thick, and the jagged rhythm is strong on the narrow ends.
- [ ] Louvre panels (grey horizontal slats) where they appear in the closeups.
- [ ] Rooftop: dark plant room (not timber), infinity pool on the sea side, glass balustrade. Compare to `v3_4k_rooftop_pool_*`.

### 8.3 Surroundings (high priority)
- [ ] **Warehouses**: large low industrial halls with blue-grey roofs next to and behind the towers. Position from `v1_drone_from_sea_warehouses` and `v3_4k_drone_oblique_*`.
- [ ] **Low white residential blocks** between and behind the towers, as seen between the towers in the front-from-sea frames.
- [ ] **Road**: ~6 lanes with a **palm median**; correct width.
- [ ] **Promenade**: light paving, **red cycle lane**, palm rows in the right places (look down from `v1_view_promenade_beach_from_tower`).
- [ ] **Beach**: correct depth; **beach bars (chiringuitos)** as low white/wood boxes with sunbeds; **small palm clusters only at the bars**; **remove any palm rows on open sand**; lifeguard posts.
- [ ] **Breakwater** (stone groyne) to the east, the **Los Guindos chimney** (~100 m, brick) and the **port cranes** further east. Check the chimney position with `17` and `v3_4k_sunset_coast_chimney_port`.
- [ ] **Roundabout** near the site if it's visible in a view.
- [ ] **Plaza**: lawns, ponds, terracotta pergolas and the communal pool, per `v3_4k_podium_pool_garden` and `v1_render_garden_pond`.
- [ ] City and mountains behind: denser mid-rise blocks and the Montes de Málaga silhouette. They don't need detail, just the right massing and colour.

### 8.4 Cameras
- [ ] Re-tune `VIEWS` so each view **matches a real reference angle** where one exists. This is the best way to get realistic results, because the AI then gets a reference with the same composition:
  - `front` ↔ `v3_4k_front_from_sea_golden_hour` (match it closely)
  - `side` ↔ `v3_4k_front_from_beach_*` or `19` (along the promenade)
  - `aerial` ↔ `v3_4k_drone_oblique_beach_road_*` / `v1_drone_from_sea_warehouses`
  - `back` ↔ `v1_render_three_towers_from_city` (city side)
  - `rooftop` ↔ `v3_4k_rooftop_pool_coast`
- [ ] Use `?dev` → orbit → **Copy current camera** to tune. Keep fov 34° and 16:9.

### 8.5 Done when
- [ ] For each view, export ↔ matching reference flicked side by side: towers, base, road, promenade, beach, neighbours and landmarks are all **in the right place and the right shape** (colour and realism don't matter, the AI does those).
- [ ] Performance: still smooth on Martin's PC (RTX 3090) and reasonable on a weaker one. Instancing, ~≤100 draw calls, baked shadows.
- [ ] Floor clicking, filters, panel and photo mode still work (test: `__towers.selectFloor(__towers.TOWERS[1].floors[11])`).
- [ ] **Re-export the 5 sunset stills** via `?dev` → ①, and put them in `exports/` (overwrite the old ones).

---

## 9. JOB 2: Build the stills generation script

### 9.1 Spec
- **File:** `gen_stills.py` plus `GEN-STILLS.bat` (installs deps, runs, pauses). Windows, Python 3.
- **Deps:** `google-genai`, `pillow`.
- **API key:** from env `GEMINI_API_KEY`, or a prompt asks for it the first time and saves it to `.env` (add `.env` to any `.gitignore`). **Never hard-code the key.**
- **Model:** `gemini-3-pro-image` (as listed in AI Studio). Check the exact ID and config field names against the current Gemini API docs before running.
- **Call shape (google-genai):**
  ```python
  from google import genai
  from google.genai import types
  client = genai.Client(api_key=KEY)
  resp = client.models.generate_content(
      model="gemini-3-pro-image",
      contents=[img1, img2, ..., prompt_text],          # PIL images first, in the exact order the prompt refers to
      config=types.GenerateContentConfig(
          response_modalities=["IMAGE"],
          image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),  # "4K" for finals
      ),
  )
  for part in resp.candidates[0].content.parts:
      if part.inline_data: open(out, "wb").write(part.inline_data.data)
  ```
- **Max 14 images per request:** image 1 = the camera frame, then up to 13 references.
- **Per view:** generate **N variants** (default 3) at 2K → `media/candidates/<view>_<n>.png`. Then a "final" mode re-runs the picked prompt and seed at **4K** → `media/<view>.jpg`, resized to 1920×1080 for the site with the 4K kept as `<view>_4k.jpg`.
- **Consistency mode:** once `front` is approved (`media/front.jpg` exists), include it as the **last** image for the other views, with the line "The last image is the approved hero shot of this project: match its colour grade, light and materials exactly".
- **CLI:** `python gen_stills.py front` · `python gen_stills.py side back --variants 4` · `python gen_stills.py all` · `--final front_2` · `--dry-run` (prints the image list and prompt without calling the API).
- **Robustness:** retry with backoff on 429/5xx, skip missing ref files with a warning (fall back from `refs/full` to `refs/preview`), log every request (view, images used, prompt hash, cost) to `media/candidates/log.csv`.
- **Cost print:** $0.134 per output image (2K), ~$0.24 at 4K (check the current price). Input images are negligible. Print a running total and ask for confirmation if a run would exceed $5.
- **Contact sheet:** after a run, write `media/candidates/<view>_sheet.jpg` with all variants side by side and the camera frame for comparison.

### 9.2 Per-view image lists (start here, tune after the first results)
Order matters: image 1 is always the camera frame `exports/still-<view>-sunset.png`.

| View | Images 2–14 (13 refs, most important first) |
|---|---|
| front | v3_4k_front_from_sea_golden_hour, v3_4k_front_from_sea_day, v3_4k_front_from_sea_blue_hour, v1_drone_from_sea_warehouses, v1_drone_from_sea_low_beach, v3_4k_front_from_beach_1, 13_photo_from_beach, sv_01_tower_base_street, v3_4k_entrance_92_dusk, 02_detail_white_plates, 03_detail_corner_stack, 20_detail_plates_from_below, v1_view_promenade_beach_from_tower |
| side | v3_4k_front_from_beach_1, v3_4k_front_from_beach_2, 19_photo_promenade, v1_view_promenade_beach_from_tower, v1_view_coast_roundabout, 15_photo_park, 16_photo_street, sv_01_tower_base_street, v3_4k_front_from_sea_golden_hour, 02, 03, 12_photo_facade_up, 20 |
| back | v1_render_three_towers_from_city, v1_terrace_city_side_1, v1_terrace_city_side_2, v3_4k_podium_pool_garden, v1_render_garden_pond, 11_photo_two_towers, 16_photo_street, sv_01_tower_base_street, v3_4k_drone_between_towers_sea, v3_4k_front_from_sea_golden_hour, 02, 03, 20 |
| rooftop | v3_4k_rooftop_pool_coast, v3_4k_rooftop_pool_2, 07_rooftop_pool_day, 08_rooftop_pool_sunset, 09_rooftop_pool_dusk, v1_render_rooftop_pool, v3_4k_view_beach_from_tower, v1_terrace_view_beach_breakwater, v3_4k_sunset_coast_chimney_port, v1_terrace_neighbour_tower, 02, 03, 20 |
| aerial | v3_4k_drone_oblique_beach_road_1, v3_4k_drone_oblique_beach_road_2, v1_drone_oblique_promenade, v1_drone_from_sea_warehouses, 14_render_aerial_promenade, v3_4k_sunset_coast_chimney_port, v1_view_coast_roundabout, v3_4k_front_from_sea_golden_hour, sv_01_tower_base_street, 02, 03, 12, 20 |

**Avoid** `01_render_hero_lamela` and `21_render_competition_lamela` for the composition-sensitive views. Their compositions hijack the camera, and they show an older design.

### 9.3 Prompt template
Build it from blocks: **LOCK + REFS + BUILDING + SURROUNDINGS + VIEW + LIGHT (+ CONSISTENCY)**.

**LOCK**
> Image 1 is a 3D layout render and is the ONLY source for composition. The output must have exactly the same camera position, height, angle, lens and framing as Image 1, and every building, road, promenade, beach and landmark must keep the same position, size and outline as in Image 1. Do not copy the camera angle, viewpoint or composition of any other image. Replace the simplified 3D surfaces with photoreal materials only.

**REFS**
> Images 2–{N} are real photographs and renders of the same place, used ONLY for materials, details, vegetation and the look of the surroundings.

**BUILDING**
> Málaga Towers by Estudio Lamela: three identical 21-storey residential towers in a straight row parallel to the coast on the Paseo Marítimo Antonio Banderas, Misericordia beach, Málaga. Every floor is ringed by thick bright-white cantilevered slab plates about one metre deep in section; their projection changes from floor to floor and from segment to segment, so each tower's outline is a jagged stack of white bands with deep shadow beneath every plate. Frameless clear glass balustrades on every plate; recessed dark grey-blue floor-to-ceiling glazing; grey horizontal-slat louvre panels in some bays. The base: a recessed dark-glass ground floor under a deep white overhang, a wide continuous white first-floor band with a row of straight vertical white posts, an entrance canopy with angled white fins and the number 92, and a low white podium wing. Flat roof with a dark grey plant room and an infinity pool on the sea side.

**SURROUNDINGS**
> Next to and behind the towers are large low industrial warehouses with blue-grey roofs and low white residential blocks. In front of the towers: a landscaped plaza with lawns, ponds and terracotta pergolas; a wide six-lane road with a palm-planted median; a promenade with light paving, a red cycle lane and rows of palm trees; then a wide golden sand beach with a few beach bars, sunbeds and small clusters of palms only at the beach bars, no palm rows on the open sand; then the Mediterranean. To the east, a stone breakwater, the tall brick Los Guindos chimney and the port cranes; inland, the city and the Montes de Málaga mountains.

**VIEW lines**
- front: *Seen from just above the sea, looking straight inland across the beach, promenade and road at the three towers standing side by side.*
- side: *Seen from the promenade to the east, looking west along the coast: palm rows, the road and the beach leading to the three towers.*
- back: *Drone view from the city side at mid height, looking over the warehouses, the plaza and the three towers to the beach and open sea beyond.*
- rooftop: *From just above the rooftop of the eastern tower: infinity pool and plant room in the foreground, the other two towers and the coastline beyond.*
- aerial: *High oblique drone view from above the sea to the south-west, looking north-east along the coast at the three towers beside the road, promenade and beach.*

**LIGHT**
> A few minutes before sunset, low warm sun from the west raking across the left faces, white plates glowing apricot, shaded faces cool blue, soft haze over the sea. Photoreal architectural photograph, natural colour, crisp detail, no people in focus, 16:9.

**CONSISTENCY** (only once front is approved)
> The last image is the approved hero shot of this project: match its colour grade, light and materials exactly.

### 9.4 QA checklist for each generated still (reject if any fail)
- [ ] Composition matches Image 1 (flick between them; the towers sit in the same pixels).
- [ ] 21 floors + base on every tower, and the base looks like `sv_01`.
- [ ] Plates are irregular and staggered, not neat rings.
- [ ] No palms on open sand; the beach bars are there; the warehouses are next to the towers.
- [ ] No logos, no text except "92", no invented extra towers.
- [ ] Sunset light consistent with the approved front.

---

## 10. After the stills (for later, manual)
Covered in GUIDE.md §2–4: Kling transitions (start + end frame, 5 s, order front → side → back → rooftop → aerial → front), optional idle loops, ffmpeg reverse and compress, and filling `CONFIG.media` in index.html. Update GUIDE.md once the script exists (stills section → "run GEN-STILLS.bat").

---

## 11. Gotchas
- **Headless testing:** in Chrome with SwiftShader (no GPU) the clip recorder only captures a few frames. It's fine on a real GPU. Stills export works headless.
- **Exports go to the browser's Downloads folder.** Move them into `exports/`.
- **The camera frame must be 16:9 at 1920×1080.** Don't change fov or aspect without re-exporting everything.
- **Google Maps imagery is outdated** (construction site). Use the `refs/video` frames as the truth.
- Keep the label **"Concept · sample data"** on the page.
- Reference photos are copyrighted; never publish them.

## 12. Open questions for Martin
1. Keep `media/aerial_candidate_01.jpg` (calibrate the aerial camera to it), or regenerate after the model fix? (Recommended: regenerate.)
2. Real tower names (the middle one is reportedly "Sierra Blanca Tower") instead of A/B/C?
3. Interiors and "view from your floor" images later? Same script, different prompts.

---

## 13. Progress log: session 2 (16 Nov 2026)

### Job 1: 3D model rebuilt (awaiting Martin's OK at the checkpoint)
Review page: `exports/review/index.html` (each new export next to its reference; raw candidates are `candidate-<view>-sunset.png`). Once Martin approves, copy them to `exports/still-<view>-sunset.png`.

**Corrections to §5 found in the references** (these override §5/§8 where they differ):
- The **big stone breakwater, the roundabouts and the empty sandy lot (campervans) are WEST of the towers.** `v1_view_coast_roundabout` / `v1_terrace_view_beach_breakwater` look west (sea on the left). East: side street, warehouses, white apartment blocks, small groynes, Los Guindos chimney (pale brick, ~1 km east), the bay and the port.
- The "92" entrance and the posts base face the **coast road, which is on the sea side** (+z) of the towers.
- **Plaza pergolas are white** (stepped, between B and the podiums), not terracotta.
- **Podiums:** A's reaches east toward B and C's reaches west toward B, two storeys with a communal pool on the roof. B has no wing.
- **Roof:** the long infinity pool runs **along the east edge (north–south)**, with the graphite two-storey plant room west of it, a small dark glazed pavilion at the pool's south end, and a timber deck.
- **Road median** is mostly trees (pines/olives) with occasional palms.
- **Section to the sea** (`v1_view_promenade_beach_from_tower`): road → blue + red lanes → ~30 m promenade (red paving, lawn/tree patches, playground, white shade pergolas) → light walkway with lamps → low dune patches with palm clusters by the beach bar → ~60 m open sand → sea.
- **Towers:** straight row, 72 m apart, glass 32×24 m (sea face ≈ 40 m with plates), ground 5.2 m + 21 × 3.3 m, plate edge 1.1 m. Measured on the front-from-sea frame: spacing/width 1.64 vs 1.66 in the photo.

**Cameras** (`VIEWS`, fov 34°, 16:9) are each solved against a reference: front ↔ `v3_4k_front_from_sea_golden_hour` (4 px RMS), side ↔ `19_photo_promenade` (west plaza looking east; the side view is **from the west**, not the east as §9.3 said), back ↔ `v1_render_three_towers_from_city`, rooftop ↔ `v3_4k_rooftop_pool_coast` (tower C roof looking ESE: chimney, port, the coast mountains; the other towers are NOT in this view), aerial ↔ `v1_drone_oblique_promenade` (all three towers whole; the v3 oblique frames crop the tops). Update the §9.3 view lines accordingly.

**Code changes in index.html:** new base (recessed ground, uniform band, deep posts `finGeo` on floor 1, thick floor-2 band; posts are pickable as floor 1), podium wings, roof layout, the whole site section rewritten with per-instance-colour InstancedMeshes (`flat`, `solid`, `city`, `roof`), coast bend toward the port east of x=1200 (`XB`, `BEND`), mountains as fog-free MeshBasic. **28 draw calls, ~242k triangles**, 60 fps (vsync cap) on the 3090.

**Camera snap fixed:** OrbitControls clamped the polar angle to 89°, so every flight ending on a view that looks *up* (front, side) snapped on the first frame after landing. Now `maxPolarAngle = 0.75π`, the ground is protected by `MIN_CAM_Y`, and leftover orbit inertia is cleared when a flight starts. Verified on all 20 view-to-view flights: 0.000 m movement after landing.

**Dev hooks** (`?dev` only): `__towers.shot(pose)` renders any `{pos,target}` at 1920×1080 and returns `{url, calls}`; `window.__cam`.

### Still open
- Martin's OK on the 5 views (checkpoint), then copy them to `exports/` and do Job 2.
- §12 questions 1–3.

### Job 2: stills script built (16 Nov 2026)
- `gen_stills.py` + `GEN-STILLS.bat` (double-click: installs deps, asks for arguments, pauses). GUIDE.md §1 now describes the script instead of AI Studio.
- **Model ID verified** with `--list-models` on Martin's key: `gemini-3-pro-image` = Nano Banana Pro (`-preview` also exists; the script falls back to it on a 404). SDK google-genai 2.31.0: `ImageConfig(aspect_ratio="16:9", image_size="2K"|"4K")`, `seed` on `GenerateContentConfig`. Prices from ai.google.dev pricing: $0.134 per 1K/2K image, $0.24 per 4K image.
- Per-view reference lists follow §9.2, adjusted to the matched cameras (side leads with ref 19, aerial with `v1_drone_oblique_promenade`). The front-from-beach frames are dropped from side because their composition is front-like. The prompt blocks are §9.3 with the corrected facts and view lines from §13.
- The images are labelled in the request ("Image 1 (camera frame): …"). The camera frame is sent as lossless PNG, references as 1600 px JPEGs (≈ 4.5 MB per request).
- Candidates go to `media/candidates/<view>_<n>.png` + `.json` (seed, prompt and images, used by `--final`), plus `log.csv` and `<view>_sheet.jpg`. `--promote` turns a 2K candidate into `media/<view>.jpg` for free.
- Tested: dry-run of all views (14 images each, no missing refs), consistency mode (hero shot becomes image 14), contact sheet, payload size. **No paid call made yet.**
- Next: Martin's go-ahead → `python gen_stills.py front` (3 × 2K ≈ $0.45) → QA (§9.4) → adjust prompt/refs → the other views.
- **Paid test 1 (front, 3 × 2K, $0.45, approved by Martin):** all 3 variants FAILED the composition lock. They came out as high oblique drone views from the SW, with 9–16 floors, an invented continuous podium, and chimney/port/breakwater pulled into the frame. Contact sheet: `media/candidates/front_sheet.jpg`. Causes: (1) the prompt listed landmarks outside the frame, so the model moved the camera to show them; (2) half the refs were elevated drone shots; (3) "layout render + references" reads as generation, not as an edit of Image 1.
- **Prompt/refs v2 (in the script now, not yet tested):** edit-style LOCK ("Turn Image 1 into a photorealistic photograph… do not move the camera"), a per-view FRAME line with the measured tower positions from the 3D (% of width/height), a VISIBLE line listing only what's in that frame, and refs limited to same-angle photos + close-up details (7–9 inputs instead of 14). Next: Martin's go-ahead for front test 2 (~$0.42).

- **Martin's feedback on test 1:** "all wrong, don't look like the real thing". He gave a $10 total budget for tests and asked for every photo to be accurate to the real tower.
- **Experiments (1 variant each):** camera frame ONLY → composition held almost perfectly. Frame + 3 refs (incl. the same-angle golden-hour photo) → composition broke again (10-floor generic towers). **Conclusion: with Nano Banana Pro, any extra image pulls the camera away; send the frame alone.** Default is now `DEFAULT_MAX_REFS = 0`; references (`--max-refs`, `--refs`) and the hero image (`--consistency`) are opt-in.
- **Rooftop** invented two towers in the sea because the shared text said "three towers": it now has its own `ROOFTOP_BUILDING` text ("the camera stands on one tower, no other tower in view").
- **Accuracy fixes found by comparing AI crops with the real golden-hour photo:** in the 3D, plate depths reduced to 1.3–3.1 m (the real outline steps only 1–2 m) and the slab edge thickened to 1.3 m (white band ≈ 40% of the floor). The frames were re-exported and all earlier candidates archived in `media/candidates/old_v1/`. In the prompt: the light is now "golden hour, sun from the WSW lighting the sea-facing facades", and the blocks between the towers are "modern 7–8 storey blocks with dark glazing and white balcony bands".
- **Composition score:** edge-map correlation between frame and output. Good variants score 0.73–0.96; one that ignored Image 1 scored 0.39. The threshold is 0.6. It's printed, logged and drawn on the contact sheets, and `--final` won't overwrite `media/` if the 4K re-run fails it. About 1 in 6 frame-only variants still breaks, so always check.
- **Output geometry:** the model's "16:9" is 2752×1536 (2K) / 5504×3072 (4K). Measured tower edges match the frame best with a plain resize (not a crop), so `media/<view>.jpg` is a straight resize to 1920×1080. A 50/50 blend of frame and still shows the plates coincide; photo-mode hover/click outlines land on the right floor (tested).
- **FINAL STILLS DONE:** front_3, side_2, back_2, rooftop_3, aerial_2 → `media/<view>.jpg` + `<view>_4k.jpg`, plugged into `CONFIG.media.stills`. All passed §9.4 QA. Known differences from reality: the light is softer/more pastel than the saturated real golden hour, and the rooftop pool reads shorter and wider than the real long lap pool. **Total spend $4.49 of the $10 budget** (`media/candidates/log.csv`; old v1 rows reuse candidate names and are told apart by timestamp).
- **GitHub:** pushed to `macekmar5-lgtm/mtowersweb` (public). `refs/`, `exports/review/`, `.env` and the candidate PNGs are git-ignored; every push is scanned for key patterns and the actual key value.
- **Next:** Kling clips (GUIDE §2), optional re-rolls of rooftop/light if Martin wants them, §12 questions.
