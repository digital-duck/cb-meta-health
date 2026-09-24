# cb-meta-health: Review and Revision of the Gemini Draft Graphs

- **Reviewer:** Claude Opus 5.5 (Claude Code)
- **Date:** 2026-09-23
- **Inputs reviewed:**
  - `docs/gemini/exercise-eating-health.pdf`: the Gemini chat that started this book
  - `public/domains/meta_health_ch01…ch06/input/graph.yaml`: Gemini's draft chapter graphs
  - `public/domains/catalog.json`: Gemini's draft catalog
- **Reference used for the expected format:** `scripts/concept_graph.py` (the `_load_yaml_graph` loader), `../cb-calculus/public/domains/*`

---

## 1. Background: what the chat actually proposed

The Gemini conversation builds, step by step, an original idea that belongs to the author:

1. **五脏操 (Five-Organ Exercises)**: five movements, each mapped to one organ and one of the Five Phases (五行):
   扩胸 → 肺/金, 扇肋 → 肝/木, 提身 → 肾/水, 扭转 → 脾/土, 深蹲 → 心/火.
2. **Three ways to order the movements**: the 相生 generating cycle (Wood → Fire → Earth → Metal → Water), a top-to-bottom anatomical order, and an organ-clock order. The chat also discussed the "YouTube" order, which starts with 扩胸 and swaps it with 扇肋.
3. **八段锦 ↔ 五脏操 mapping**: the five exercises work as isolation drills for Baduanjin's compound forms. 第1式 is the overall regulator. The chat also covers the 10-minute daily dose, breath timing, 松紧交替, and 收功.
4. **Eating as internal exercise (饮食即内脏运动)**: a meal is a workout for the digestive organs and circulation. Blood flow to the gut rises after eating; in TCM terms, the 脾胃运化 engine starts up. The practical rules follow from that framing: warm up (chew slowly, relax first), control the load (七分饱), and protect recovery (warm, cooked food).
5. **Poor food, poor habits, and stress follow the same logic**: junk food is like training under a useless load; overeating and late eating are like training with bad form; stress blocks the flow. In TCM terms that is 肝主疏泄 and 肝木克脾土; in physiology, fight-or-flight activity pulls blood away from the gut.
6. **The synthesis, 内调一元论 (the Unified Internal Conditioning Framework)**: mental state → mindful eating → rest after the meal → Baduanjin, organized as a 24-hour plan.

These points are the book's own contribution, and the graphs should be built around them.

---

## 2. Review findings on the Gemini drafts

### 2.1 Schema mismatch (the drafts could not load)

Gemini used this format:

```yaml
nodes:
  - id: ...
    title: ...
    type: primitive | composite
    prerequisites: [...]
    summary: ...
```

The ConceptBook loader (`scripts/concept_graph.py::_load_yaml_graph`) expects the cb-calculus format:

```yaml
domain: meta_health_chNN
primitives:
  name: {defines: ..., tier: 0}
concepts:
  name: {defines: ..., composed_of: [...], tier: N}
applications:
  name: {defines: ..., needs: [...], tier: N}
```

The loader reads only `primitives`, `concepts`, and `applications`, so **every Gemini chapter loaded as an empty graph**. Gemini's `composite` type also doesn't exist in this schema; the valid kinds are `primitive`, `concept`, and `application`.

### 2.2 The catalog had the wrong shape

- The frontend (`src/pages/Home.js`, `Domain.js`) expects `catalog.json` to be a **list** of domain entries with fields such as `id`, `name`, `capstone`, `default_level`, `tags`, `has_navigator`, `books`, and `generated_concepts`. Gemini wrote an object (`{project, dimensions, domains}`).
- Its level names (`introductory/intermediate/advanced`) don't match the app's levels (`intro/core/college/research`, see `scripts/level_style.py`).
- Its model name `claude-3-7-sonnet` is out of date and isn't used anywhere in this app.

### 2.3 The content drifted away from the chat

The drafts read like a generic strength-and-conditioning syllabus: hinge/squat, push/pull, progressive overload, tendon remodeling, workout-timed nutrition, mitochondrial biogenesis. None of the book's actual ideas appeared as nodes: 五脏操, 八段锦, eating as internal exercise, 肝木克脾土, the organ clock, 四气五味. TCM showed up only in ch06, as a single vague "triad" node.

### 2.4 The chapters were too thin

Each chapter had 3–5 nodes (22 in total). cb-calculus chapters have 25–49 nodes. With so few nodes, each generated book would be only a few sections long.

### 2.5 Factual issues in the chat that are worth correcting

| Claim in the chat | Correction |
|---|---|
| Organ clock: "Lung strongest 5–7 AM" | 寅时 **3–5 AM** is Lung; 5–7 AM (卯时) is Large Intestine. |
| Organ clock: "Liver 1–3 PM" | 丑时 **1–3 AM** is Liver; 1–3 PM (未时) is Small Intestine. The "organ-clock sequence" of the exercises in the chat depends on this error. |
| 扩胸 ↔ 第3式 (first mapping) | 第2式 左右开弓似射雕 is the natural chest-opening / Lung-Metal match. 第3式 is named for the Spleen and Stomach. The later mapping in the chat already moved toward 第2式. |
| "内脏等张运动 (internal **isometric** exercise)" | 等张 means *isotonic*, not isometric. The simpler terms 内脏运动 / "internal exercise" are used instead. |
| "胃火（命门之火）" powers digestion | 胃火 is a disorder in TCM (stomach heat). The digestive "fire" is **脾阳**, which is supported by 命门之火 / 肾阳. |
| Baduanjin "developed during the Song Dynasty explicitly around Five Element organ theory" | Overstated. Baduanjin is first recorded in the Song dynasty, and the modern 健身气功 set was standardized in 2003. The systematic Five-Phase mapping is **the author's synthesis**, which is exactly why it counts as a contribution. |
| "Re-routes 20–30% of total cardiac output" after a meal | Reworded: the gut and liver (splanchnic circulation) receive about a quarter of cardiac output at rest, and blood flow to the intestines roughly doubles after a meal. |

---

## 3. Revision: the new book structure

The book grew from 6 chapters to **9 chapters with 214 nodes**, organized as foundations → movement → eating → mind → time → synthesis. The **五行 correspondence table runs through every chapter**: organ → exercise → 八段锦 form → flavor/food → emotion → organ-clock time → season. Chapter 9 brings it together in a single integration table.

| Ch | Title | P / C / A | Nodes | Edges | Final concept (capstone) |
|---|---|---|---|---|---|
| 1 | TCM Foundations: Yin-Yang, Qi-Blood, and the Five Phases (中医基础) | 8 / 17 / 1 | 26 | 47 | `five_phase_body_map` |
| 2 | The Physiology Lens: Breath, Circulation, Fascia, and Core (生理视角) | 7 / 18 / 1 | 26 | 42 | `dual_lens_translation` |
| 3 | The Five-Organ Exercises (五脏操) | 11 / 12 / 1 | 24 | 40 | `five_organ_routine_design` |
| 4 | Baduanjin: The Eight Brocades (八段锦) | 10 / 16 / 1 | 27 | 44 | `daily_baduanjin_practice_plan` |
| 5 | Eating as Internal Exercise (饮食即内脏运动) | 7 / 17 / 1 | 25 | 42 | `mindful_meal_protocol` |
| 6 | What We Eat: Food Quality, Four Natures, Five Flavors (四气五味) | 9 / 15 / 1 | 25 | 37 | `five_phase_meal_design` |
| 7 | Stress, Emotion, and the Flow of Qi and Blood (情志与气血) | 9 / 14 / 1 | 24 | 31 | `stress_resilience_routine` |
| 8 | Rhythms: Sleep, the Organ Clock, and the Seasons (天人相应) | 4 / 13 / 1 | 18 | 30 | `personal_daily_rhythm_schedule` |
| 9 | The Unified Internal Conditioning Framework (内调一元论) | 10 / 8 / 1 | 19 | 26 | `daily_meta_health_protocol` |

P / C / A = number of primitives / concepts / applications (application nodes are the practical, applied concepts).

### 3.1 Chapter highlights

- **Ch1, TCM foundations.** 阴阳, 气/血/津液/精/神, the 相生 and 相克 cycles and their distortions (相乘相侮), 五脏/六腑/表里, the twelve meridians, 三焦, 丹田, 先天/后天, 气滞血瘀, 心肾相交, the Liver–Spleen relationship, and 阴平阳秘.
- **Ch2, the physiology lens.** Breathing mechanics, cardiac output and how blood is distributed between organs and muscles, the skeletal-muscle and respiratory pumps, lymph, the autonomic nervous system and heart-rate variability (HRV), fascial lines, core pressure, squat mechanics, alternating tension and relaxation, and body awareness (interoception). The final concept, `dual_lens_translation`, translates TCM claims into physiology and rates each correspondence as *mechanistic*, *plausible*, or *metaphorical*.
- **Ch3, 五脏操.** One node per movement, each with both a physiological and a TCM explanation. It also covers the 涌泉 point, a summary movement table, the three ways of ordering the movements (相生, breath-first/"YouTube", top-to-bottom), the sealing finish (收势), and safety modifications.
- **Ch4, 八段锦.** All eight forms under their standard names; 三调; coordinating breath with movement; 松紧结合; 收功; the 八段锦 ↔ 五脏操 mapping; the practice dose (10 minutes, 1–2 times a day); and an evidence-base node covering what trials do and do not show.
- **Ch5, eating as internal exercise.** The core chapter. It sets physiology (the head/cephalic phase of digestion, satiety signals, blood flow to the gut after meals, the load that digestion puts on the heart, gut motility, first-pass metabolism in the liver, the blood-glucose response) next to TCM (胃主受纳腐熟, 脾主运化, 升清降浊). These lead to `eating_as_internal_exercise` and then to warm-up, load pacing (七分饱), digestive "overtraining", and gentle movement after meals (饭后百步走).
- **Ch6, food.** Energy, protein across the lifespan, carbohydrate and fat quality, the fiber–microbiome link, whole versus ultra-processed food (NOVA), 四气, 五味 (sour → Liver, and so on), 五色, the warm-cooked-food principle, 湿/痰浊, "junk load", meal timing, the balanced plate, 药食同源, and 体质.
- **Ch7, stress and emotion.** The HPA stress axis, acute versus chronic stress, allostatic load (cumulative wear from stress), stress and digestion, the gut–brain axis, 七情, 五志 and the five organs, 肝主疏泄, 肝气郁结, **肝木克脾土** (the TCM counterpart of stress shutting down digestion), emotional eating, breath as the bridge to the nervous system, releasing Liver qi through movement, 调心, and HRV self-monitoring.
- **Ch8, rhythms.** Light and the body clock, the cortisol/melatonin cycle, sleep architecture and metabolic repair, meal timing by the clock (chrononutrition), exercise timing, day–night 阴阳, the **correct** 子午流注 hours, sleeping before 子时, breakfast in 辰时, and 四时养生 with 春养肝…冬养肾.
- **Ch9, synthesis (内调一元论).** 内外兼修, the mind–body–digestive loop, the Five-Phase integration table, "train, don't overload" applied to the organs, habit formation, personalization, self-observation, and an **evidence-and-safety lens** (see a doctor for diabetes, heart disease, pregnancy, or medication questions). It ends with the 24-hour Meta-Health protocol.

### 3.2 Design rules applied

- **Each chapter stands alone.** Anything a chapter needs from an earlier chapter is declared again as a primitive tagged "(from Chapter N)", the same approach cb-calculus uses.
- **Every node leads to the chapter's final concept.** The book generator only includes nodes on the path to the capstone, so a disconnected node would never be generated. The build script enforces this.
- **Chinese terms stay inside the English definitions** (e.g. `脾主运化`) so zh generation keeps the TCM terminology exact.
- **Speculative claims are marked as speculative** in the definitions (e.g. whether twisting "massages" the gut, and the link between dampness and metabolic overload). The LLM takes its framing from these definitions, so this is how the book stays honest as a health book.
- **Every `defines` value uses the folded block style (`>-`)**, never a quoted string: the text sits on indented lines under the key and loads back as one line of text. The build script handles this with a `Folded` string type.
- **Node IDs are readable English plus pinyin** (e.g. `rib_fanning_shanlei`, `organ_clock_ziwu_liuzhu`). The UI shows node labels as `id.replace('_', ' ')`.
- **The strength-training topics were deliberately dropped** (progressive overload, tendon/bone remodeling, mitochondrial biogenesis). The book is about gentle practice, eating, and whole-body balance. If wanted, those topics could return as an optional Ch10.

---

## 4. Files changed

| Path | Change |
|---|---|
| `public/domains/meta_health_ch01…ch06/input/graph.yaml` | Rewritten in the ConceptBook schema with the new content |
| `public/domains/meta_health_ch07…ch09/input/graph.yaml` | **New** chapters |
| `public/domains/meta_health_ch0*/output/graph.html` | Generated with `concept_graph.py visualize --format html` |
| `public/domains/catalog.json` | Rebuilt as a list of 9 entries: `default_level: core`, `tags: ["health", <theme>]`, `has_navigator: true`, `has_book: false`; chapter names start with "元健康 Meta-Health ChN" |
| `src/i18n.js` | `app.title` = 元健康 Meta-Health (en) / 元健康 (zh), with a tagline in each language. `t()` now falls back to English one key at a time, so the zh block only has to override the keys it translates |
| `index.html` | Page `<title>` and meta description changed to 元健康 Meta-Health |
| `docs/gemini/graph_drafts_v0/` | The original Gemini drafts (6 yaml files plus catalog.json), kept for comparison |
| `docs/gemini/build_graphs_v1.py` | One editable file that writes all 9 graph.yaml files and catalog.json |

### About `build_graphs_v1.py`

It holds all chapter content in one place. It **computes the tier (depth level) of each node** from its prerequisites and checks that:

- every prerequisite is defined in the same chapter,
- there are no cycles or duplicate names,
- every primitive is used,
- every node leads to the chapter's final concept.

It writes to the repo's `public/domains/`. Once written, `graph.yaml` is still the file the app reads. Running the script again **overwrites** the catalog's `books` and `generated_concepts` lists, so after book generation starts, edit `graph.yaml` directly or merge the catalog carefully instead.

Note: `sync_from_spl.sh` still has an empty `LEVEL_MAP`. The graphs here were authored in this repo, not synced from SPL.py, so the script isn't needed. To rebuild a navigator directly:

```bash
python3 scripts/concept_graph.py --domain public/domains/<id>/input/graph.yaml \
  visualize --format html --output public/domains/<id>/output/graph.html
```

---

## 5. Book title: 元健康 Meta-Health

- **English:** *Meta-Health: Movement, Eating, and Mind as One Practice*
- **Chinese:** 《元健康：运动、饮食与心神的一体修炼》

Why 元: it is the standard translation of "meta" (as in 元数据), it means origin or first principle, and it echoes 元气 (vital energy in TCM). It also ties to the framework's name, 内调一元论. The subtitle heads off two misreadings: "metabolic health" and Meta, the company.

## 6. Verification

- `python3 scripts/concept_graph.py --domain <graph.yaml> stats --strict` → **Reducible: True** for all 9 chapters, meaning every concept and application traces back to that chapter's declared primitives.
- `visualize --format html` succeeded for all 9 chapters.
- **Not yet done:** the frontend (`npm run dev`) wasn't opened, and no book content was generated.

---

- A regex spelling pass in an earlier revision damaged some words (e.g. "Exercise" became "Exercize", and "raise"/"rise" became "raize"/"rize"). These were fixed and every remaining "-ize" word was checked.

## 7. Suggested next steps

1. Run `npm run dev` and look through the nine graphs. Rename or merge nodes to your taste.
2. Generate **Ch3 (五脏操)** and **Ch5 (饮食即内脏运动)** first. They are the most original chapters and the best test of the style profile at the `core` level.
3. Generate the `zh` versions early. The TCM terminology is where the translation is most likely to drift.
4. Consider adding a `source` entry to each chapter in the catalog that credits the originating conversation and the author, so the chapters are marked as original content rather than derived from a textbook.
5. Optional later chapters: **Ch10, Strength and Aerobic Training for Longevity**, and a **Ch0, How to Read This Book**, which would explain the dual TCM/physiology lens and how to judge the evidence.
