# 元健康 Meta-Health — TODO: regenerate zh and evaluate the generation fixes

- **Created:** 2026-09-24
- **Context:** `docs/gemini/review-revise-by-opus-5-5.md` §7 has the full root-cause write-up.

## Why

The first full generation (core · sonnet · en + zh, 2026-09-23/24) had three content
problems, concentrated in the Chinese text:

| # | Problem | Status |
|---|---|---|
| 1 | A broken formula (`\frac` missing) in `eating_as_internal_exercise` (zh, ch05 and ch09) | ✅ Fixed in both pages and in the section cache |
| 2 | The ch09 payoff translated "meta-health" as 代谢健康 (metabolic health) and leaked raw node IDs | ✅ Fixed. It was a workflow bug: the payoff got only the bare target ID. Both ch09 payoffs were regenerated. |
| 3 | Invented formulas everywhere, much worse in zh (168 display equations vs 60 in en), e.g. `健康 ⟺ 阴阳平衡 ∧ 五行通畅` | ✅ Both regenerated (v2): zh 168 → 9, en 60 → 9 display equations, 0 invented |

Cause of #3: `style_profiles.infer_subject_rigor()` matched no keyword in `meta_health_*`, so it
fell back to `rigorous` ("formal notation… include it whenever the concept calls for it"). Core's
"Simple rule or pattern" step then pushed the model to state rules as formulas.

## Fixes applied

In both **cb-meta-health** and **concept-book-base** (base not yet committed):

| File | Change |
|---|---|
| `spl/build_concept_book.spl` | LaTeX-delimiter rules for write/refine/payoff (from `conceptbook-app`); a **notation-honesty** rule (equations only for real, established relationships; complete LaTeX with `\frac{…}{…}`; no snake_case IDs in prose); the **payoff now gets the target's label, definition and direct prerequisites** |
| `spl/tools.py` | New `prereq_labels` tool; `apps_list` returns labels, not IDs; MathJax loads `mathtools` (for `\xrightleftharpoons` etc.) |
| `spl/style_profiles.py` | New **`health`** subject-rigor tier (keywords: health, nutrition, wellness, fitness, tcm, qigong): real quantities OK, never formalize qi / yin-yang / Five Phases / emotions, label traditional claims as traditional. Core's rule step now says "in words; as a formula only if the subject has a real one". |
| `scripts/batch_gen_domains.py` | Passes `style` (it was silently ignored); raises spl3 limits (60 iterations / 120 calls / 600k tokens); recognizes `book_{target}_{lang}.html` |
| `scripts/README-test_gen.md` | Documents the above |

Not yet ported: **`conceptbook-app`** still has the payoff bug and none of the formula rules.

## Plan: archive zh v1, regenerate zh v2, compare

We archive rather than overwrite for two reasons:

- **The v1 content is the "before" sample** for evaluating the fixes.
- **The run becomes resumable.** With a fresh progress file and no `--force`, finished chapters
  are skipped and unfinished ones are generated. `--force` would redo everything after a rate-limit
  stop. Deleting the files alone wouldn't help either: without `--skip-cache` the old sections
  would come straight back from the cache.

### 1. Archive the v1 zh output

```bash
conda activate spl123 && cd ~/projects/digital-duck/cb-meta-health
mkdir -p archive/zh-v1
for d in public/domains/meta_health_ch0*; do
  mv $d/output/core.zh archive/zh-v1/$(basename $d)
done
```

Layout afterwards: `archive/zh-v1/meta_health_chNN/sonnet/html/*.html`. Add `archive/` to
`.gitignore` if it shouldn't be committed. `catalog.json` needs no change: it keeps the zh paths,
which get refilled as each chapter finishes. Until then the 中文 view shows "not generated yet".

### 2. Regenerate zh v2 (overnight)

```bash
python scripts/batch_gen_domains.py -f scripts/domains-meta-health.txt \
    --model sonnet --level core --language zh --skip-cache \
    --progress-file scripts/progress_zh_v2.json \
    --log-file logs/meta_health_zh_v2.log 


# run in background
nohup python scripts/batch_gen_domains.py -f scripts/domains-meta-health.txt \
    --model sonnet --level core --language zh --skip-cache \
    --progress-file scripts/progress_zh_v2.json \
    --log-file logs/meta_health_zh_v2.log > logs/meta_health_zh_v2.out 2>&1 &
```

- `--skip-cache` is **required**. The cache key contains the style *name* (`core`), not the prompt
  text, so without it the v1 sections are reused.
- **Don't** pass `--force`.
- If it stops on a Claude rate limit, re-run the **same** command after the reset.
- Check that the `Queue` lines show `style=core`.

#### Generation timing (from `logs/meta_health_*.log`)

Per-chapter times are the `✓ done (Ns)` values, meaning spl3 generation time only. Wall clock
also includes any Claude session-limit pauses.

| Chapter | en | zh v1 | zh v2 |
|---|---:|---:|---:|
| ch01 TCM foundations | 4m 20s | 5m 23s | 5m 21s |
| ch02 Physiology lens | 4m 16s | 5m 34s | 5m 17s |
| ch03 五脏操 | 2m 16s | 2m 54s | 5m 04s |
| ch04 八段锦 | 3m 13s | 4m 11s | 5m 55s |
| ch05 Eating as internal exercise | 3m 34s ¹ | 4m 37s | 5m 15s |
| ch06 Food 四气五味 | 3m 25s | 4m 38s | 5m 13s |
| ch07 Stress & emotion | 3m 02s | 3m 42s | 5m 14s |
| ch08 Rhythms | 2m 26s | 3m 04s | 3m 52s |
| ch09 内调一元论 | 1m 39s ² | 2m 05s ² | 4m 01s |
| **Total generation** | **28m 11s** | **36m 08s** | **45m 12s** ⁴ |
| Wall clock | 23:59 → 01:04 (65 min) ³ | 01:04 → 01:40 | 06:41 → 07:26, no rate-limit stop |

¹ 9 of ch05's sections were cached from the earlier UI generation.
² ch09 is fastest because most of its sections are concepts that earlier chapters already
generated (`eating_as_internal_exercise`, `five_phase_meal_design`, …). The section cache is
keyed by concept name, so they are reused across chapters. zh v2 runs with `--skip-cache`, so
this reuse is off, and ch09 will take longer.
³ Includes a 34-minute Claude session-limit pause after ch05 (00:19 → 00:53).
⁴ zh v2 is 25% slower than zh v1. `--skip-cache` turned off cross-chapter section reuse (ch09:
4m 01s vs 2m 05s), and v2 sections are about 10% longer.

Notes:
- **Speed:** about 3 minutes per chapter for en at Core level, roughly 2× faster than
  college-level physics (~6 min/chapter). zh is about 25% slower than en.
- **zh v1 status:** its `✗ … was not written` lines were the false failures caused by the
  missing `_zh` filename suffix (since fixed). Every book was actually written, and the times
  above are real generation times.
- **zh v2 estimate:** about 36–40 min of generation, finishing around 07:20–07:25 if no session
  limit hits.
- **zh v2 restart:** the log shows two `Batch gen` starts (06:40:15 and 06:41:20). The first run
  stopped after about 25 s (its spl3 trace stops growing at 06:40:41), so only the 06:41 run
  generated content. This is cosmetic: one extra log line and an orphan trace file.

To fill in the zh v2 column when the run finishes:

```bash
grep -hE "Queue|✓ done|✗|Batch complete|Stopped" logs/meta_health_zh_v2.log
```

### 3. Evaluate

```bash
python scripts/eval_generated_content.py --dir v1=archive/zh-v1 --dir v2=public/domains
```

Counts per chapter:

| Metric | Meaning |
|---|---|
| `display` | display equations (`$$…$$`) |
| `inline` | inline math (`$…$`) |
| `broken` | malformed equations (unbalanced braces, `}}{` without `\frac`) |
| `ids` | snake_case node IDs leaking into prose |
| `metabolic` | 代谢健康 / "metabolic health" in the book payoff |

Then spot-read a few pages in the UI, especially **ch01** (TCM foundations), **ch05** and **ch07**,
the chapters with the most invented formulas in v1.

**Baseline** (measured 2026-09-24, after fixes #1/#2 were applied; the original v1 also had
`broken`=2 and `metabolic`=1):

| chapter | en display | en inline | zh v1 display | zh v1 inline |
|---|---:|---:|---:|---:|
| ch01 TCM foundations | 10 | 40 | 24 | 26 |
| ch02 Physiology lens | 13 | 97 | 22 | 100 |
| ch03 五脏操 | 10 | 51 | 16 | 40 |
| ch04 八段锦 | 4 | 18 | 16 | 42 |
| ch05 Eating as internal exercise | 3 | 48 | 22 | 90 |
| ch06 Food 四气五味 | 11 | 44 | 23 | 93 |
| ch07 Stress & emotion | 6 | 37 | 19 | 56 |
| ch08 Rhythms | 1 | 26 | 16 | 35 |
| ch09 内调一元论 | 2 | 13 | 10 | 24 |
| **Total** (214 pages each) | **60** | **374** | **168** | **506** |

**What success looks like:**
- zh v2 `display` drops to roughly the en level (≈60) or below.
- The formulas that remain are real ones: kcal, heart rate, cardiac output, glucose, time.
- No formulas for qi, yin-yang, the Five Phases or emotions.
- `broken`, `ids` and `metabolic` stay at 0.

Some `inline` math is legitimate (units, numbers, ranges), so judge it by reading rather than by
the count alone.

#### Evaluation task: zh v1 vs zh v2 (run when v2 is done)

- [x] **Confirm v2 is complete:** the log ends with `Batch complete — 9 generated`, and every
      `scripts/progress_zh_v2.json` entry is `done`.
- [x] **Run the metrics:**
      `python scripts/eval_generated_content.py --dir v1=archive/zh-v1 --dir v2=public/domains`
      and fill in the results table below.
- [x] **Classify the remaining v2 formulas** (at least ch01, ch05, ch07):
      - real quantity or established relationship (kcal, heart rate, cardiac output, glucose, time), or
      - still invented (a formula for qi, yin-yang, the Five Phases, emotions, "balance")?
- [x] **Spot-read v1 vs v2 side by side** for the same concepts, e.g. `harmony_as_health` (ch01),
      `eating_as_internal_exercise` (ch05), `stress_resilience_routine` (ch07). Did anything *get
      worse*: less clear, less concrete, lost its practice problem, or wrong TCM terminology?
- [x] **Check that traditional claims are labeled as traditional** (the new `health` tier), and
      that no scientific-sounding certainty has been added.
- [x] **Check terminology:** 元健康 is used for Meta-Health, never 代谢健康 (outside genuine
      metabolic-health contexts, such as ch08 `sleep_and_metabolic_repair`).
- [x] **Allow for run-to-run variance:** v1 → v2 changes both the prompts and the LLM sample. If
      the drop is borderline (e.g. less than 30%), regenerate one chapter twice with the same
      prompts to see how much the counts move by chance alone.
- [x] **Write a verdict:** accept v2 / tweak the prompts and rerun / partial (list chapters).

Results (evaluated 2026-09-24, after zh v2 finished at 07:26):

| chapter | zh v1 display | zh v2 display | zh v1 inline | zh v2 inline | v2 invented formulas (by reading) |
|---|---:|---:|---:|---:|---|
| ch01 TCM foundations | 24 | **0** | 26 | 2 | none |
| ch02 Physiology lens | 22 | **2** | 100 | 32 | none: `Q = HR × SV`, `V_E = V_T × f` |
| ch03 五脏操 | 16 | **0** | 40 | 11 | none |
| ch04 八段锦 | 16 | **0** | 42 | 11 | none |
| ch05 Eating as internal exercise | 22 | **1** | 90 | 23 | none: `CO = HR × SV` |
| ch06 Food 四气五味 | 23 | **4** | 93 | 18 | none; 1 borderline: `寒 < 凉 < 平 < 温 < 热` (an ordinal scale, not a law). Others: glycemic load, energy balance, kcal/g |
| ch07 Stress & emotion | 19 | **0** | 56 | 19 | none |
| ch08 Rhythms | 16 | **0** | 35 | 5 | none |
| ch09 内调一元论 | 10 | **2** | 24 | 25 | none: `HR_max ≈ 220 − 年龄` (twice) |
| **Total** | **168** | **9 (−95%)** | **506** | **146 (−71%)** | **0 invented, 1 borderline** |

v2 `broken` = 0, `ids` = 0, `metabolic` = 0 (all targets met).

**Inline math changed in kind, not just amount.**
- **v1:** mostly variables of invented models: `A_{sym}`, `A_{para}`, `S(t)`, `I(t)`,
  `\theta_h`, `\propto`, `\Delta P`.
- **v2:** almost entirely numbers with units (`100 mg/dL`, `150 bpm`, `70%`, `600 kcal`), plus
  standard physiology symbols (HR, SV, CO, V_T, the circadian period τ ≈ 24.2 h).
- **Symbols checked in context:** `\Rightarrow` (an arrow in a plain-language rule) and
  `=`/`\times` (in a real cardiac-output hint) are fine.

**No over-correction** (168 unique sections each):

| | v1 | v2 |
|---|---:|---:|
| Median section length (Chinese characters) | 429 | 471 (+10%) |
| Sections with a practice problem | 168 | 168 |
| Traditional claims labeled as traditional | 17 | 104 |
| Evidence mentions (研究表明, 证据, …) | 21 | 86 |

**Side-by-side reading:**
- **`harmony_as_health` (ch01):** v1's `健康 ⟺ 阴阳平衡 ∧ 五行通畅`, and its practice problem
  about why "the formula" fails, are gone. v2 cites the source correctly (阴平阳秘，精神乃治,
  《黄帝内经》), says in one sentence that this is a traditional framework with no scientific
  measure, then explains why it is still useful (亚健康/未病). Honest without being preachy.
- **`eating_as_internal_exercise` (ch05):** v1's proportionality formula (which was the broken
  `\frac`) is replaced by the same rule in words: preparation, load, recovery. It adds a correct
  caveat that 脾胃 is a TCM functional concept, not the anatomical organs.
- **`stress_resilience_routine` (ch07):** v1's `消化效率 ∝ 1/(1+k·压力)` is gone. The four steps
  are concrete (breathing 4 s in / 6 s out, 10–15 min screen-free), traditional (肝主疏泄) and
  established (breathing and sleep lower stress hormones) are kept apart, and it states plainly
  that it is not a cure.

**Issues found (editorial, not blocking):**
1. **Headings are in English on zh pages** ("Harmony As Health"), in both v1 and v2. The heading
   and TOC label come from the node ID via `concept_label()`, not from a translation. Fix
   options: a translated-label lookup in `write_section`, or a `label_zh` field in `graph.yaml`.
2. **ch07 `stress_resilience_routine`** suggests 扩胸 as a liver-releasing movement. In the book's
   own mapping 扩胸 is Lung/Metal; the Liver movements are 扇肋 and 攒拳怒目 (form 7). This is
   an editing-pass item, or tighten the node's `defines` to name the movements.
3. `HR_max ≈ 220 − 年龄` is a rough population estimate. An editor might add "estimate" where
   it's used as a guideline.

**Run-to-run variance:** not needed. A 95% drop, with 0 invented formulas remaining, is far
beyond sampling noise.

**Verdict: ✅ Accept zh v2.** The fixes worked: the invented formulas are eliminated, the evidence
labeling improved a lot, and length and practice problems didn't regress. The English content
should get the same regeneration. Checked for ch01/ch02/ch06, its 60 display equations include
clearly invented ones:
- `J_total(t) = J_prenatal − D(t) + ∫R(τ)dτ` (essence, 精)
- `Qi = f(movement, warmth, …)`
- `g⁵(x) = x` (generating cycle)
- `Q = E/C` (junk load)
- `cost_digest ∝ (T_body − T_food) + raw/fiber penalty`

They sit alongside real ones: `CO = HR × SV`, `Q ∝ r⁴` (Poiseuille), `P₁V₁ = P₂V₂`, RMSSD,
glycemic load and energy balance.

### 4. Afterwards

- [x] Record the v2 numbers and a verdict in this file (see the evaluation task above).
- [x] Fix English headings on zh pages (evaluation issue 1). See §5.
- [x] Archive en v1 → `archive/en-v1`. See §5.
- [x] **Regenerate en** (completed 08:31 after one session-limit stop) and evaluate with
      `python scripts/eval_generated_content.py --dir v1=archive/en-v1 --dir v2=public/domains --variant core.en`.
- [x] After the en run: rebuild the ch05 UI book `book_postprandial_glucose_response.html` from
      the cache (0 LLM calls), and drop the stale `pdfs` catalog entry (`concept_liver_metabolic_role.pdf`,
      archived in `archive/en-v1/meta_health_ch05/sonnet/pdf/`). Re-export the PDF from the UI.
- [ ] Editing pass: ch07 liver-movement slip (evaluation issue 2).
- [ ] Delete `archive/zh-v1` (and later `archive/en-v1`) once v2 is accepted.
- [x] Commit the concept-book-base changes from the first port (formula/payoff/script fixes).
- [ ] Commit the second concept-book-base port: localized labels, context-hash cache key, and
      book-index UI strings (see §5).
- [ ] Port the payoff, formula, label and cache-key fixes to `conceptbook-app`, which has diverged:
      it has its own `style_profiles.py` tiers (`social`) and Chinese-character tools.

## 5. Localized headings, the cache-key bug, and the en regeneration (2026-09-24, 07:30–)

### 5.1 English headings on zh pages: fixed, with no regeneration

**Cause:** headings, page titles and book TOC entries all came from the node ID
(`concept_label()` → "Harmony As Health"), in every language. The model was also told to begin
each section with that English heading.

**Fix:**

| Where | Change |
|---|---|
| `docs/gemini/concept_labels.yaml` (new) | en + zh display label for all 168 concepts. English labels drop the pinyin suffixes ("Blood (Xue, 血)" instead of "Blood Xue"). |
| `docs/gemini/build_graphs_v1.py` | Merges them into every node as `labels: {en, zh}`, and fails if any concept has no label |
| `spl/tools.py` | `localized_label()` / `_label_for()` (graph label → en label → title-cased id); `apps_list` and `prereq_labels` take a language; `write_concept_html` normalizes the section's leading `##` to the localized label when the node has one for that language (otherwise keeps the old bare-ID-only behavior, so books without labels are unaffected); `build_book_index` uses localized TOC and title strings plus `_BOOK_UI` for "Contents" / "Payoff" / "Concept Book" (zh: 目录 / 学以致用 / 概念书) |
| `spl/build_concept_book.spl` | Section loop and payoff use `localized_label(..., @language)`, so new runs write the localized heading directly |

**Result:** the zh pages were re-rendered **from the cache** (0 LLM calls, about 25 s).
All **223 zh pages** (214 sections + 9 books) have Chinese headings, titles and TOC entries.

### 5.2 A cache-key bug found along the way: fixed, zh v2 recovered

**Symptom:** the first cache-only re-render changed the *body text* of some pages. For example,
ch01 `harmony_as_health` showed a different text.

**Cause:** the content-cache key was `(concept, language, style, model)`, with no chapter or
definition in it. 46 concepts are declared in more than one chapter: later chapters re-declare
earlier ones as primitives, with a shorter "(from Chapter N)" definition. So:
- **Without `--skip-cache`:** a later chapter silently reused the earlier chapter's section.
  This is why ch09 generated fastest, and why the broken `\frac` appeared in both ch05 and ch09.
- **With `--skip-cache`:** the last chapter to run overwrote the shared slot. The zh v2 ch09
  run (07:22) replaced ch01's `harmony_as_health`, so re-rendering ch01 pulled in ch09's variant.
  Confirmed in the spl run logs: 06:41 (ch01) has the original text, 07:22 (ch09) the new one.

**Fix:** the new `section_params()` tool adds a hash of the concept's `defines` (`ctx`) to the
key, for sections and payoffs. Different definitions get separate entries, and editing a
`defines` automatically invalidates that section. Consequence: all older cache entries stop
matching, so the next run of any domain regenerates everything once.

**Recovery of zh v2 (0 LLM calls):** each chapter's full v2 output was in its spl run log
(`spl/cookbook/74_concept_book/logs-spl/…-064121.md` through `…-072230.md`). Sections were mapped
back to concept IDs by position in the teaching order. All 9 section counts matched, and every
heading difference was just the model's own Chinese name for the right concept (e.g. 膈式呼吸 =
diaphragmatic breathing). They were stored under the new keys, then zh was re-rendered: 0 cache
misses. ch01 and ch09 now each show their own `harmony_as_health` again. The zh metrics are back
to 9 display / 145 inline (146 at evaluation time; one inline item differs).

### 5.3 Ported to concept-book-base (not yet committed)

`spl/build_concept_book.spl`, `spl/tools.py` (labels, `section_params`, `_BOOK_UI`), plus a
note in `scripts/README-test_gen.md`. `spl3 validate` passes. **Note for derived apps:** the
cache-key change means their first run after upgrading regenerates everything once.

### 5.4 en v1 archived

`archive/en-v1/meta_health_chNN/sonnet/html/` holds 224 HTML pages: 214 sections, 9 chapter
books, and the UI-generated ch05 `book_postprandial_glucose_response.html`. The ch05 PDF export
`sonnet/pdf/concept_liver_metabolic_role.pdf` is archived with them.

### 5.5 en v2 regeneration: complete (after one session-limit stop) and evaluated

The first attempt (07:43) hit a Claude session limit at 07:46, partway through ch01
(`You've hit your session limit · resets 11am (America/New_York)`). **No chapter was completed.**
On disk: ch01 has 17 of its 26 en sections; ch02–ch09 have no en pages (v1 is archived), so the
English view shows "not generated yet" for them until the run completes.

Note: the two runs at 07:55 (`--log-file logs/meta_health_en.log` / `meta_health_zh.log`) used the
**default** progress file, which marks everything `done`, so they only skipped chapters; nothing
was generated or changed. Always pass `--progress-file scripts/progress_en_v2.json` for this pass.

**Resume (after 11am ET): same command, but WITHOUT `--skip-cache`.**

```bash
python scripts/batch_gen_domains.py -f scripts/domains-meta-health.txt \
    --model sonnet --level core --language en \
    --progress-file scripts/progress_en_v2.json \
    --log-file logs/meta_health_en_v2.log > logs/meta_health_en_v2.out 2>&1
```

- **Why no `--skip-cache`:** the 17 finished ch01 sections are cached under the new per-context keys,
  generated with the new prompts, so reusing them is correct and saves their LLM calls. Every
  other section misses anyway, because the old v1 entries (keyed without `ctx`) no longer match.
- Don't restore `archive/en-v1` into `public/` in the meantime. The script would then see existing
  output and skip those chapters.
- Expect about 35–45 min. If the limit hits again, re-run the same command.

**Preliminary result (ch01, the 17 sections generated so far, same 17 concepts in v1):**

| | v1 | v2 |
|---|---:|---:|
| Display formulas | 8 | **0** |
| Inline math | 33 | **0** |

The invented formulas are gone: `J_total(t) = J_prenatal − D(t) + ∫R(τ)dτ` (essence_jing),
`Qi = f(movement, warmth, …)` (qi), `g⁵(x) = x` (generating cycle), `f: zang → fu` (zang_fu_pairing).
The new English labels work: e.g. heading and title "Qi (气)".

**en baseline (v1)** for the full evaluation: 60 display / 374 inline, with invented formulas including
`J_total(t) = J_prenatal − D(t) + ∫R(τ)dτ` (精), `Qi = f(movement, warmth, …)`, `g⁵(x) = x`,
`Q = E/C` (junk load) and `cost_digest ∝ (T_body − T_food) + raw/fiber penalty`.

**Completion:** the resumed run (07:59 → 08:31, `--progress-file scripts/progress_en_v2.json`,
no `--skip-cache`) generated all 9 chapters with 0 failures. ch01 reused its 17 cached sections
(17 hits, 10 misses = 9 sections + payoff). Generation time: 32m 04s (ch01 1m 33s, ch02 4m 08s,
ch03 3m 52s, ch04 4m 19s, ch05 4m 04s, ch06 4m 14s, ch07 3m 42s, ch08 3m 01s, ch09 3m 11s),
plus about 2.5 min in the interrupted first attempt.

#### en v1 vs v2 results (evaluated 2026-09-24)

```bash
python scripts/eval_generated_content.py --dir v1=archive/en-v1 --dir v2=public/domains --variant core.en
```

| chapter | en v1 display | en v2 display | en v1 inline | en v2 inline |
|---|---:|---:|---:|---:|
| ch01 TCM foundations | 10 | **0** | 40 | 0 |
| ch02 Physiology lens | 13 | **4** | 97 | 21 |
| ch03 五脏操 | 10 | **0** | 51 | 0 |
| ch04 八段锦 | 4 | **0** | 18 | 4 |
| ch05 Eating as internal exercise | 3 | **1** | 48 | 5 |
| ch06 Food 四气五味 | 11 | **3** | 44 | 0 |
| ch07 Stress & emotion | 6 | **0** | 37 | 0 |
| ch08 Rhythms | 1 | **0** | 26 | 0 |
| ch09 内调一元论 | 2 | **1** | 13 | 2 |
| **Total** | **60** | **9 (−85%)** | **374** | **32 (−91%)** |

v2 `broken` = 0, `ids` = 0, `metabolic` = 0.

**All 9 remaining display formulas are real, established relationships:** cardiac output (×2),
Boyle's law `P₁V₁ = P₂V₂`, alveolar ventilation `V_A = (V_T − V_D) × f`, RMSSD (the standard HRV
measure), glycemic load, energy balance, kcal per gram, and the Karvonen target-heart-rate formula.
**0 invented.** Inline math is joint angles, worked-example numbers (`V_T = 500`, `f = 12`) and
standard symbols (HR, SV, CO, RR_i).

**No over-correction** (214 sections each):

| | en v1 | en v2 |
|---|---:|---:|
| Median section length (words) | 273 | 284 |
| Sections with a practice problem | 214 | 214 |
| Tradition labels ("traditional", "in TCM", …) | 68 | 437 |
| Evidence mentions (study, research, evidence, trial) | 62 | 155 |

**Spot-read:**
- **`essence_jing`:** v1's `J_total(t) = J_prenatal − D(t) + ∫R(τ)dτ` is replaced by a clear
  "starting balance plus daily deposits" analogy, with a good practice problem.
- **`five_flavors_wuwei`:** flavor → organ → action is explained in words, labeled as traditional,
  and then linked to modern nutrition's independent warning about excess salt and the kidneys.

**Minor style issue:** the jump in tradition labels (about 2 per section) is mostly honest framing,
but some sections state the caveat twice in adjacent sentences (e.g. `essence_jing`). Trim in the
editing pass. If it bothers you across the book, a one-line prompt tweak would do it: "state a
concept's traditional/evidence status once per section".

**Verdict: ✅ Accept en v2.** It matches zh v2 (168 → 9 display, 506 → 145 inline): the invented
formulas are eliminated in both languages, and length and practice problems didn't regress.

#### Combined before/after (both languages)

| | v1 display | v2 display | v1 inline | v2 inline | invented in v2 |
|---|---:|---:|---:|---:|---:|
| en | 60 | 9 | 374 | 32 | 0 |
| zh | 168 | 9 | 506 | 145 | 0 (1 borderline) |

#### Cleanup done after the run

- Rebuilt the ch05 UI book `book_postprandial_glucose_response.html` from the cache (9 hits,
  0 LLM calls) and re-registered it.
- Removed the stale `pdfs` entry for `concept_liver_metabolic_role.pdf` from `catalog.json`. The v1
  PDF is in `archive/en-v1/meta_health_ch05/sonnet/pdf/`; re-export from the UI if needed.
- Catalog check: all 19 books (9 en + 9 zh + the ch05 UI book) and 428 concept pages (214 × 2)
  exist on disk.
