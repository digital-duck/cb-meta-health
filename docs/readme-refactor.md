# Graph-IDE refactor — what changed and how to roll it out

This documents the 2026-09-13 backport from `cb-chemistry-ide` (a derived app used as
the design prototype) into this base template. Everything below is now in `main`'s
working tree here; validate it by generating a brand-new concept-book from this base
before rolling it out to any existing derived app.

## Summary

The old design split the app into two pages — `/domain/:id` (graph only) and `/book`
(content only) — joined by header nav links. The new design is one consolidated
Graph-IDE page: graph on the left, generated content (with its own TOC) on the right,
driven by one shared Model/Level/Language/Generate control set. Alongside that UI
rework, a same-day Opus 5 code review of the whole change surfaced 19 findings (2
HIGH security, 8 MEDIUM, 9 LOW) which are folded into this backport too — a fresh
concept-book built from this base gets both the new UX and the hardening in one shot.

## What changed

**Frontend (`src/`)**
- `pages/Domain.js` is now the single consolidated IDE page: top domain picker (+
  explicit **Load** button), graph left, content right.
- New `components/ContentPanel.js` replaces the old `ConceptPanel.js` + `BookPage.js`:
  Model / Level / Language / Refresh / **Generate** / **Export PDF** controls, a
  flattened alphabetical TOC (concept/application/**primitive** nodes on the selected
  node's prerequisite path — primitives now get full Generate/content treatment, not
  just a `defines` blurb), and content resolution with a stale-response guard.
- `components/GraphViewer.js` trimmed to the graph iframe + a `getPath()`/`selectNode()`
  bridge for `ContentPanel.js`. A CSS-only relayout hides `graph.html`'s own
  learning-path/explanation panels and turns its Notes sidebar into a collapsible
  bottom drawer — the drawer's own `localStorage` note-taking JS is untouched.
- Deleted: `pages/BookPage.js`, `components/ConceptPanel.js`, `components/BookViewer.js`,
  the `/book` and `/graph` routes, the Header nav links to them.
- New `lib/paths.js` (path-schema builders) and `lib/contentExists.js` (shared
  "does this generated page exist yet?" check) — previously duplicated logic.
- `.gitignore`: fixed a generic `lib/` rule that was silently swallowing `src/lib/`.

**Backend security (Opus review HIGH findings)**
- `scripts/start-api.sh` binds `127.0.0.1`, not `0.0.0.0` — the backend now holds
  user-supplied LLM API keys and has side-effecting GET endpoints, so LAN/CORS exposure
  is a real risk, not a theoretical one.
- `api/app.py`'s CORS narrows from wildcard to the actual `DEV_PORT`-derived dev
  frontend origin(s), with restricted methods/headers.
- New `api/services/path_safety.py` (`safe_segment`/`safe_optional_segment`/
  `assert_within`) validates every `domain`/`target`/`level`/`language`/`model` query
  param before it touches a filesystem path — wired into `generate.py` and `pdf.py`.

**Backend correctness (MEDIUM/LOW findings + related fixes)**
- **Level selector now actually works.** `build_concept_book.spl` has no `@lvl` input,
  only `@style` — `--param lvl=...` was a silent no-op and every request generated at
  the hardcoded default style regardless of the level picked in the UI. New
  `scripts/level_style.py` is the single level→style map (with a math-tag-aware
  `research`→`research_applied` fallback), imported by both `api/services/executor.py`
  (web UI) and `scripts/batch_generate.py` (CLI batch runs) so they can't drift apart.
- `@model` added to the SPL content-cache key (`build_concept_book.spl`'s
  `@_params_json`) — the cache is keyed only by concept+params, not by output
  directory, so two models could otherwise silently share one cache slot.
- Payoff (capstone) generation is now cached (previously regenerated on every request)
  and only runs for `kind="application"` targets — a concept/primitive target clicked
  directly in the IDE never displays the payoff anyway, so generating one was a pure
  wasted LLM call.
- `api/services/pdf_svc.py`: catalog writes now go through the locked
  `catalog_lock.update_catalog()` instead of a raw read/write race; PDF dedup keys on
  the full `(target, level, language, model)` tuple with update-in-place; "not
  generated yet" is a 404, not a 500; error messages no longer leak absolute server
  paths.
- New `api/services/adapters.py` — the single adapter-name ↔ env-var ↔
  Settings-field table (previously duplicated 2-3x across `executor.py`/`settings.py`).
- Settings page gets direct-adapter support: Anthropic / OpenAI / Gemini / OpenRouter,
  each with a password-style API Key field (never echoed back, only a boolean
  "is it set" flag — which now also falls back to checking the bare, non-`CB_`-prefixed
  env var, since generation already picks those up). Keys are in-memory only; a
  `--reload` or process restart wipes them — pre-seed durably via `.env`'s
  `CB_*_API_KEY` vars instead.
- `PUT /api/settings`'s `llm` value is now validated against known adapter prefixes
  up front, instead of failing deep inside a later `spl3` subprocess.
- **Compare Cache feature removed entirely** — `api/routers/compare.py`,
  `api/services/compare_svc.py`, the Settings page's Compare Cache section, and
  `CB_COMPARE_CACHE_TTL` are all gone.
- `spl/tools.py`: `target_kind()` (drives the payoff gating above), `normalize_bool()`
  (so `@skip_cache` accepts `"true"`/`"1"`, not just exact `"yes"`), and
  `build_book_index()` no longer renders an empty `<section></section>` for a
  payoff-less (non-application) target. SPL footer credit rephrased and hyperlinked to
  the SPL.py repo, opening in a new tab.
- `scripts/concept_graph.py`: fixed the vis.js node tooltip rendering raw HTML as
  literal text instead of formatted content (`title` must be a DOM element to render
  as HTML, not a string).
- Zoom In/Out buttons added to the graph view, with scale clamped to `[0.1, 4]`.

**`CLAUDE.md`** was rewritten to describe this architecture (it was still documenting
the old split-page / `ConceptPanel` design) — this is the doc future derived apps and
Claude Code sessions read first, so it needs to be accurate before anything else.

## What was deliberately NOT touched

Base had independently diverged from the common ancestor on several of these files —
its own `concept_context()` tool in `spl/tools.py`, language-suffix handling in
`api/services/catalog_svc.py`, a self-locating `spl3` fix in `start-api.sh`, and
`claude-sonnet-5` model-name bumps. All of that was preserved; this refactor was
layered on top, not pasted over it. Chemistry/physics-specific tweaks to
`scripts/sync_from_press.py` and `scripts/batch_gen_domains.py` from the prototype
app were left out as out-of-scope for this UI/UX refactor, as was any prototype-specific
branding (`README.md`, `package.json` name) or dev-notes content.

## Existing generated content needs no migration

This refactor changes UI/backend logic only — already-generated concept/book HTML and
`catalog.json` entries can be copied into a migrated repo unchanged and will keep
rendering and resolving correctly:

- `src/lib/paths.js`'s `parseLevelLangModel()` derives level/lang/model by
  regex-parsing the file path itself, and tolerates a missing model segment (a legacy
  path without a model subfolder just parses `model` as `''`).
- `ContentPanel.js`'s catalog lookups only require the fields old `catalog.json`
  entries already have (`{name, label, file, model}`); the newer `language` field is
  optional and falls back to being derived from the path when absent.
- `contentExists.js`'s existence check is `text.includes('spl-credit') ||
  text.includes('Generated by')`. The footer text was rephrased ("Generated and
  Powered by...", no longer containing the literal substring "Generated by"), but the
  `class="spl-credit"` on the `<footer>` element is unchanged, so the check still
  passes via the first branch.
- Nothing in the migration opens, rewrites, or regenerates already-written HTML files
  — `write_concept_html()`/`build_book_index()` only run on *new* generation.

**One caveat — not about the HTML files, but about SPL's separate Layer-2 LLM content
cache:** `build_concept_book.spl` now includes `@model` in the cache-key params
(`@_params_json`). Pre-migration cache rows were written without `model` in their
params, so the first time a given concept+level+language is *re-generated* (without
`skip_cache`) after migration, it'll be a cache miss against the old row and cost a
fresh LLM call rather than reusing it — working as intended (it's what stops two
different models from silently sharing a cache slot), but worth knowing before
re-generating in bulk. It has no effect on simply viewing already-generated pages.

## Validating from this base

1. `npm install && npm run dev` — frontend-only smoke test (no book generation).
2. `conda activate spl123 && pip install -r requirements-api.txt && bash
   scripts/start-api.sh` in one terminal, `npm run dev` in another.
3. Generate a brand-new domain end to end and confirm:
   - The consolidated page (graph left, content+TOC right) renders with no
     learning-path/explanation panels inside the graph iframe, and Notes is a
     collapsed bottom drawer.
   - Clicking a concept/application/primitive node populates the TOC and either shows
     existing content or "not generated yet" with **Generate** enabled.
   - Changing Level actually changes the generated prose's style (e.g. `intro` reads
     noticeably more Feynman/conversational than `college`).
   - **Export PDF** and the Settings page's adapter API-key fields both work.
4. `python3 -c "from api.app import app"` under the `spl123` env, and
   `spl3 validate spl/build_concept_book.spl`, as cheap sanity checks before spending
   real LLM calls.

## Migration plan — existing concept-books

None of these have been touched by this refactor yet. Each was independently
diverged from this base to varying degrees (its own domain content, and in some cases
its own bug fixes never upstreamed here — check before blindly overwriting, the same
way this backport itself preserved `concept-book-base`'s own divergence from
`cb-chemistry-ide`).

**`cb-zinets` is a special case, not a template fork.** Inspecting it (rather than
just checking for `ContentPanel.js`/git status, which is all the other 9 needed)
turned up its own auth system (`auth.py`/`auth_svc.py`/`Login.js`), a chat feature
(`chat.py`), an async task queue (`tasks.py`/`task_worker.py`), a SQLite DB layer
(`db.py`), and custom-named pages (`DomainGraph.js`/`BookContent.js`, not
`Domain.js`/`BookPage.js`) — it had already built out the "Book page layout" extension
point this base's `CLAUDE.md` describes, on its own. A full UI-consolidation migration
there needs deliberate, scoped-down handling (see decision below), not the same
mechanical process as the other 10. The other 10 (`cb-college-physics`, `cb-linalg`,
`cb-calculus`, `cb-statistics`, `cb-algorithms`, `cb-data-structure`,
`cb-graph-intro`, `cb-biology`, `cb-data-science`, `cb-chemistry`) all still match the
plain pre-refactor template shape exactly (`About.js`/`BookPage.js`/`Domain.js`/`Home.js`/
`Settings.js`; `compare.py`/`domains.py`/`generate.py`/`pdf.py`/`settings.py`) —
straightforward candidates for the process below. Recommended order: `cb-college-physics`
first to rehearse the steps, then the remaining 9, then `cb-zinets` last with extra
care (or backend-fixes-only — see its own note in the table).

**Note on `cb-chemistry` vs. `cb-chemistry-ide`:** these are two separate repos, not
the same app at different states. `cb-chemistry-ide` is the derived app that was used
to *prototype* this refactor (see the Summary above) and already has the new
Graph-IDE UI. `cb-chemistry` (no `-ide` suffix) is a distinct, independently-seeded
app — same underlying chemistry content (OpenStax *Chemistry 2e*, 21 domains, no
`source` field populated in any domain's `catalog.json` entry — same gap as
`cb-biology`/`cb-data-science` before their About-page fix) — that still has the old
split-page template shape and has never been touched by this refactor. It goes through
the same mechanical process as the other 9 template-shape repos, not a copy from
`cb-chemistry-ide` (that app's own independent divergence, if any, hasn't been audited).

Suggested per-repo steps (mirrors how this backport was done, and how
`cb-college-physics` — the first one done — was actually migrated):
1. None of these repos share a git commit ancestor with this base (each was seeded by
   copying files in, not `git clone`d) — `git diff <ancestor> HEAD` doesn't work across
   repos here. Instead, for each file this refactor touches, diff the target repo's
   current version against this base's *pre-refactor* version (`git show
   <base-commit-before-this-refactor>:<path>` in this repo) to see whether the target
   has its own independent divergence to preserve.
2. Port file by file: straightforward copy where the target repo matches base's
   pre-refactor version; manual merge (base's new code + target's own fixes) where it
   doesn't. `cb-college-physics` turned out to have its own real fix (applied in two
   places) that neither this base nor `cb-chemistry-ide` had — see "Fixes found during
   migration" below;
   check for the same pattern in each remaining repo rather than assuming only this
   base's own divergences (noted above) are the ones that matter.
3. Drop Compare Cache if still present (`api/routers/compare.py`,
   `api/services/compare_svc.py`, `CB_COMPARE_CACHE_TTL`, Settings page section).
4. Update the repo's own `CLAUDE.md` `## Architecture` section the same way this base's
   was rewritten, preserving any domain-specific sections the repo has appended (intro
   paragraph, content-scope notes, roadmap) — don't blindly overwrite the whole file.
5. Rebuild (`npm run dev` / `vite build`) and re-import the backend
   (`python3 -c "from api.app import app"`) before generating anything.
6. Generate at least one concept end to end per level to confirm the level→style fix
   actually changes output, and confirm existing generated content (committed HTML
   under `public/domains/`) still renders — this refactor changes generation code, not
   the schema of already-generated pages, so old content should keep working unchanged.
7. Commit as its own PR/commit, separate from any unrelated in-flight work in that repo.

### Fixes found during migration (worth backporting here too)

**Quick summary — live validation session, 2026-09-14, against `cb-college-physics`.**
All items below were fixed in this base and propagated identically to all 9 repos in
the table (all 10 codebases confirmed byte-identical on every touched file as of this
writing). None of these are `cb-college-physics`-specific except where noted, so
already-validated repos don't need re-checking, but any repo not yet validated should
expect these fixes to already be in place — no need to re-report them.

| # | Issue | Fix |
|---|---|---|
| 1 | Non-English concept catalog name kept the `_{language}` filename suffix (e.g. `observation_zh`), a different catalog identity than the English entry | `mark_book_generated()`/`_mark_generated()` strip the suffix before recording `name`/`label` |
| 2 | Generating the same target/model/language at a *different* level silently deleted the earlier level's catalog entries (dozens of entries lost fleet-wide, recovered via backfill) | catalog dedup keyed off the exact file path (encodes level) instead of `(model, language)` alone |
| 3 | Freshly-generated non-English content showed "Not generated yet" right after Generate finished | `ContentPanel.js` refetches `catalog.json` after Generate; `conceptUrl()`/`bookUrl()` now append the `_{lang}` suffix in their guess fallback |
| 4 | Export PDF 404'd for any non-English content (pre-dates the Graph-IDE refactor) | `pdf_svc.py` now appends the same `_{lang}` suffix when locating the HTML and naming the PDF |
| 5 | Generated pages' own embedded `nav.toc` sidebar duplicated the app's TOC | `ContentPanel.js` injects CSS into the content iframe hiding `nav.toc` |
| 6 | *(`cb-college-physics` only)* Same "Source: ..." attribution repeated on all 34 domain pages | Moved to a single section on the About page; not applicable to repos without one shared source |
| 7 | TOC kind-tag emoji | 🎯/⚛️ → 🌸 (application) / 🌱 (primitive) |
| 8 | Notes entry box (`#notes-textarea`) ate most of the bottom drawer, squeezing the notes history list | Shrunk to one line (32px) via injected CSS in `GraphViewer.js`; standalone `graph.html` unaffected |
| 9 | "Not generated yet" empty-state message was two lines and easy to miss | Rewritten to one line: "⚠️ Missing content for model=X, level=Y, language=Z, click **Generate** button to create" |

`cb-college-physics` had independently fixed a real bug this base never had: when
generating in a non-English language, `mark_book_generated()`/`_mark_generated()`
recorded the concept's catalog `name`/`label` *with* the `_{language}` filename suffix
still attached (e.g. `observation_zh`/`Observation Zh`), making it a different catalog
identity than the English `observation` entry rather than the same concept in another
language — this produced "Please generate the concept book for observation zh first"
even though the current Model/Level/Language selectors were already correct. Present
in `api/services/catalog_svc.py` and `scripts/batch_generate.py`'s own
`_mark_generated()` (the latter also reused by `scripts/batch_gen_domains.py`).
**Ported back into this base** in both places — verified with a direct
`mark_book_generated()` call against a `concept_observation_zh.html` fixture, which now
correctly records `name: "observation"` (not `"observation_zh"`).

**Cross-level catalog overwrite bug** — found live during the user's own
post-migration validation of `cb-college-physics` (a concept generated at `college`
level, model `sonnet`, showed as "Not generated yet" in the app even though the file
existed on disk and had the `spl-credit` marker). Root cause: `mark_book_generated()`'s
(and `_mark_generated()`'s) dedup logic for `generated_concepts` only matched on
`(model, language)`, not level — so generating the *same* target/model/language
combination at a *different* level (e.g. `research` after `college`) silently dropped
every catalog entry for the earlier level's own generated concepts, even though those
HTML files were completely untouched on disk. The `books` list had a parallel but
opposite-shaped bug: its "already recorded" check also ignored level, so a second
generation of the same target/model/language at a new level was silently never
appended to `books` at all (blocked by the earlier level's entry matching the same
triple). Fixed in both `api/services/catalog_svc.py` and
`scripts/batch_generate.py`'s `_mark_generated()` by keying off the *exact output file
path* instead of the `(target/model, language)` triple — the file path already encodes
level, language, and model, so this is both correct and simpler than adding an
explicit `level` field. **Ported to all 9 already-migrated repos below** (`catalog_svc.py`
copied directly from this base's fixed version in every repo; `batch_generate.py`'s
`_mark_generated()` patched in place, preserving each repo's own surrounding code) —
plus a one-time backfill script was run against each repo's live `catalog.json` to
recover the specific entries the bug had already silently dropped (re-derived by
scanning `output/{level}.{lang}/{model}/html/` on disk against what the catalog listed,
adding back anything the catalog was missing without touching any HTML files). This
recovered entries in `cb-linalg`, `cb-calculus`, `cb-data-science` (the largest — dozens
of missing book/concept entries across dev-testing sweeps at multiple levels), and
`cb-data-structure`; `cb-college-physics`, `cb-algorithms`, `cb-graph-intro`, and
`cb-biology` needed no backfill. **This base itself was never live-generated against**
(no `catalog.json` with real generation history), so the bug never manifested here —
worth a similar backfill scan on any concept-book repo not in this list before trusting
its `catalog.json` fully, if it has ever been generated at more than one level for the
same model.

**Stale in-page catalog + missing language suffix on freshly-generated content** — found
live during the user's own validation of `cb-college-physics`: generating a concept in a
non-English language (zh) via the in-app Generate button completed successfully (file
written, catalog updated server-side) but the panel kept showing "Not generated yet"
right after. Root cause, two compounding bugs in `ContentPanel.js`/`lib/paths.js`:
(a) the panel's `conceptIndex` is built once from the `catalog.json` snapshot the page
loaded with and was never refreshed after a Generate completed, so a node generated
*this session* is invisible to the catalog-aware fast path; (b) the fallback path this
forces the panel onto — `conceptUrl()`/`bookUrl()` guessing the conventional filename —
never appended spl/tools.py's `_{language}` filename suffix for non-English content, so
even the guess was wrong (`concept_units.html` guessed vs. `concept_units_zh.html`
actually on disk). Fixed both: `lib/paths.js`'s `conceptUrl`/`bookUrl` now append the
language suffix exactly like the backend's own suffix logic; `ContentPanel.js`'s
Generate `done` handler now re-fetches `catalog.json` and rebuilds `conceptIndex` in
place before re-resolving, so freshly-generated content is picked up immediately via
the fast path instead of relying on the (now-fixed) guess at all.

**Export PDF also broken for non-English content** — same missing-suffix bug,
independently present in the backend: `api/services/pdf_svc.py`'s `generate_pdf()`
looked for `concept_{target}.html`/`book_{target}.html` unconditionally, so any
non-English PDF export 404'd ("Not generated yet") even though the HTML genuinely
existed under `_{lang}`-suffixed name. This one predates the Graph-IDE refactor
entirely — pre-refactor `pdf_svc.py` had the same gap, it just never appended a model
segment either, so nothing had exercised the non-English case before now. Fixed by
computing the same suffix and applying it to both the HTML lookup and the output PDF
filename. Verified end-to-end against the exact failing case
(`generate_pdf('college_physics_ch01', 'units', 'college', 'zh', 'sonnet')` →
`{'ok': True, 'file': 'output/college.zh/sonnet/pdf/concept_units_zh.pdf'}`).

**Old embedded page TOC hidden in the content iframe** — every generated HTML page
ships its own `nav.toc` sidebar (spl/tools.py's own "← back / chapter contents" panel),
which duplicated this app's own left-hand TOC now that the Graph-IDE redesign shows
both side by side. `ContentPanel.js` now injects a small `<style>` into the iframe's
document on load (same-origin) hiding `nav.toc` and letting `main` fill the width. This
is cosmetic-only — the generated HTML itself is untouched, so it still looks correct
when opened standalone outside the app.

All four of these fixes were made directly in this base and then propagated identically
to all 9 already-migrated repos (`lib/paths.js`, `ContentPanel.js`,
`api/services/pdf_svc.py` copied from base's fixed versions); all 9 re-verified with
`vite build` and `python3 -c "from api.app import app"` afterward.

One fix from this same validation round was **repo-specific, not backported**: in
`cb-college-physics`, the per-domain "Source: College Physics 2e by OpenStax..."
attribution banner was removed from `Domain.js` and replaced with a single "Content
source" section on the About page — all 34 domains in that repo cite the identical
source, so showing it on every domain page was pure repetition. This only makes sense
because that repo's domains share one source; base's generic per-domain attribution
(shown only when `domain.source` is set) is still the right default for a repo whose
domains cite different sources, so it was left as-is in this base and in every other repo.

**Update, 2026-09-14:** the same repetition existed in every other single-source repo
in the table above — `cb-linalg` (9 domains, all citing FCLA), `cb-algorithms` (12,
Erickson's *Algorithms*), `cb-calculus` (6, OpenStax *Calculus Volume 1*),
`cb-data-structure` (13, Morin's *Open Data Structures*), `cb-statistics` (13, OpenStax
*Introductory Statistics 2e*), and `cb-graph-intro` (8, van Steen's *Graph Theory and
Complex Networks*) each had one `source` object shared identically across every domain
in their `catalog.json`. Applied the same fix to all six: removed the `domain.source`
block from `Domain.js`, added a "Content source" section to `About.js` reusing the
existing `source.attribution` text verbatim (not reworded). `cb-graph-intro`'s source
has no `url` (empty string in the catalog), so its About page renders the title as
plain text instead of a broken empty `<a href="">` link — Domain.js's old per-domain
code had that same empty-href bug, but it wasn't worth replicating into new code.
`cb-zinets` has no `source` field on any domain (special-cased, not touched).

**Correction, same day:** `cb-biology` and `cb-data-science` were initially assumed to
have no source at all, but both are in fact single-source OpenStax repos too — their
`catalog.json` entries just never had a `source` field populated (confirmed OpenStax
authorship from each PDF's own front matter in `concept-book-press/input/`:
`Biology-2e.pdf` → `openstax.org/details/books/biology-2e`,
`Principles-of-Data-Science.pdf` → `openstax.org/details/books/principles-data-science`,
both CC BY 4.0). Added the same "Content source" section to each repo's `About.js`
(no `Domain.js`/`catalog.json` change needed — since `source` was never set, no
per-domain banner was ever rendered there to remove).

Also corrected `cb-graph-intro`: its `catalog.json` `source.url` was an empty string
for all 8 domains (the van Steen PDF has no OpenStax-style landing page), but the PDF's
own front matter (`concept-book-press/input/graph-theory/graph-theory-and-complex-networks-an-introduction.pdf`)
names the author's companion site, `http://www.distributed-systems.net/gtcn/`
(see `concept-book-press/input/graph-theory/readme.md`'s `## Ingest` section for the
non-OpenStax attribution rationale) — populated that URL in all 8 catalog entries and
linked the title to it in `About.js` instead of rendering it as plain text.

All nine repos (the original six plus these three corrections) rebuilt clean with
`npm run build`.

**Follow-up, same day — motivation paragraph.** The user's underlying goal for moving
attribution to the About page isn't just crediting the source — it's that each
concept-book is meant to be used *alongside* the original text, not as a standalone
replacement, and the source link is how a learner gets there to go deeper (full proofs,
worked examples, exercises). Added a second, identical `<p>` under every repo's
"Content source" section (all 9: `cb-college-physics`, `cb-linalg`, `cb-algorithms`,
`cb-calculus`, `cb-data-structure`, `cb-statistics`, `cb-graph-intro`, `cb-biology`,
`cb-data-science`) making this explicit:

> This concept-book is a companion to the original text, not a replacement for it. The
> graph and generated sections here help you see how the ideas connect and where to
> start, but the full depth — proofs, worked examples, exercises, nuance — lives in the
> source. Follow the link above to read it directly; that is where deep mastery
> actually happens.

Every repo's source link now resolves to a real, working URL (confirmed above for
`cb-biology`/`cb-data-science`/`cb-graph-intro`; the other six already had one). Base's
per-domain attribution (`Domain.js`, shown only when a domain sets `source`) was left
untouched — it's a multi-source template default, and the companion motivation lives in
each domain's own free-text `source.attribution` field there rather than a fixed
About-page paragraph. All 9 rebuilt clean with `npm run build`.

**Follow-up, same day — section order.** The "Content source" section (both
paragraphs) was originally appended near the bottom of the About page, after "The
content engine". Moved it up to directly follow "How to use it" (i.e. second section
on the page, right after the intro) in all 9 repos — a learner deciding whether to use
this concept-book should see what it's sourced from and how to go deeper into the
original before reading about the content engine or Chinese-character founding
use-case. Final order in all 9: intro → How to use it → **Content source** → The
founding use-case → The content engine → Open source. All 9 rebuilt clean with
`npm run build`.

**Follow-up, same day — founding use-case moved to last, with a cb-zinets pointer.**
"The founding use-case: Chinese Characters" section explains *why* concept-book exists
(the Chinese-character-radical insight) but isn't what a learner needs before deciding
whether to use a given domain — moved it to the very last section on the page, after
"Open source", in all 12 repos that carry this boilerplate About page (`concept-book-base`
itself, the 9 repos above, plus `cb-chemistry` and `cb-chemistry-ide` — the two that
hadn't otherwise been touched by this refactor round). Also appended a pointer to
[`cb-zinets`](https://github.com/digital-duck/cb-zinets) — the concept-book fully built
around this founding use-case — so a learner curious about it can dig in further.
Final order everywhere: intro → How to use it → (**Content source**, where present) →
The content engine → Open source → **The founding use-case: Chinese Characters**.
`cb-zinets` itself has a custom About page (no `founding use-case`/`Content source`
boilerplate) and wasn't touched. All 12 rebuilt clean with `npm run build`.

Three further UI-polish requests came out of the same session, all general (not
`cb-college-physics`-specific) and backported to this base + all 9 repos identically:

- **TOC kind-tag emoji swapped**: `ContentPanel.js`'s `_TOC_KIND_TAG` changed from
  🎯 (application) / ⚛️ (primitive) to 🌸 (application) / 🌱 (primitive).
- **Notes entry box shrunk to one line**: `graph.html`'s own `#notes-textarea` is a
  fixed 100px tall — sized for the old standalone page's roomy right-column layout, but
  inside the Graph-IDE's much shorter bottom drawer it alone ate most of the drawer's
  height, squeezing the notes history list below it down to a couple of visible rows.
  `GraphViewer.js`'s injected `_injectLayout` style now also overrides
  `#notes-textarea` to a single-line `32px`, freeing the rest of the drawer for history.
  Scoped to the injected CSS only — the standalone `graph.html` page (opened directly,
  outside the app) keeps its original roomier textarea.
- **"Not generated yet" message rewritten to one line**: was two lines, "Not generated
  yet for **sonnet** / **college** / **zh**." / "Click Generate to create it." — now
  "⚠️ Missing content for model=**sonnet**, level=**college**, language=**zh**, click
  **Generate** button to create" (`ContentPanel.js`'s `resolveContent()` empty-state
  branch).

| cb-name | migrated | is_valid | in_github | notes |
|---|---|---|---|---|
| cb-zinets | Yes | Yes | Yes (`digital-duck/cb-zinets`) | **Not a template fork** — has its own auth, chat, async task queue, and SQLite DB layer; already implements a custom `book/` page split. Migrate last, and scope it down (backend fixes only, or a hand-reviewed frontend pass) rather than the mechanical process used for the other 9. |
| cb-college-physics | Yes (uncommitted — see below) | YES. Backend/CLI verified: `python3 -c "from api.app import app"`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-college-physics`) | First migration done, mirroring this base's own backport. Also picked up its own independently-fixed language-suffix catalog bug (see "Fixes found during migration") not yet ported back to this base. Not committed — review the working tree before committing/pushing. |
| cb-linalg | Yes (uncommitted — see below) | YES.  Backend/CLI verified: `python3 -c "from api.app import app"`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-linalg`) | Second repo done. Was missing the spl3-self-locate `start-api.sh` fix this base already had (added it, plus the bind change) — otherwise a clean template match. |
| cb-graph-intro | Yes (uncommitted — see below) | Yes - Backend/CLI verified: `python3 -c "from api.app import app"`, `import batch_generate`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-graph-intro`) | Eighth repo done. Had 2 pre-existing unrelated local changes (`.env.example`, `README.md`) — left untouched, confirmed still present after migration. No custom `api/config.py` validator. Was missing both the language-suffix catalog fix and the `model_seg` fix in `catalog_svc.py` (was identical to base pre-refactor, picked up both via direct copy) — missing them in `batch_generate.py`'s `_mark_generated()` too (added language-suffix fix there). Missing spl3-self-locate `start-api.sh` fix (added it, plus bind change). |
| cb-calculus | Yes (uncommitted — see below) | Yes - Backend/CLI verified: `python3 -c "from api.app import app"`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-calculus`) | Third repo done. Didn't have the language-suffix catalog fix (added it, same as base's own gap before this round) — otherwise a clean template match. |
| cb-statistics | Yes (uncommitted — see below) | Yes. Backend/CLI verified: `python3 -c "from api.app import app"`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-statistics`) | Fourth repo done. Already had the language-suffix catalog fix and spl3-self-locate independently — a clean template match. |
| cb-data-science | Yes (uncommitted — see below) | YES. Backend/CLI verified: `python3 -c "from api.app import app"`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-data-science`) | Fifth repo done. Had its own dev-testing default `@domain_yaml`/`@target`/`@style`/`@log_dir` values in `build_concept_book.spl` — preserved those while merging in skip_cache/model/target_kind. Missing the language-suffix fix and self-locate `start-api.sh` fix — added both. Still referenced by name in this base's `CB_SPL_WHILE_MAX_ITER` comment as a domain with longer capstone sections — worth an extra check that longer sections still generate cleanly post-migration. |
| cb-algorithms | Yes (uncommitted — see below) | YES. Backend/CLI verified: `python3 -c "from api.app import app"`, `import batch_generate`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-algorithms`) | Sixth repo done. Had its own `field_validator`-based path resolution in `api/config.py` (preserved, matched cb-linalg's pattern). `catalog_svc.py` was identical to base pre-refactor so picked up both fixes (language-suffix + model_seg) via direct copy; `batch_generate.py`'s `_mark_generated()` was missing the language-suffix fix (added it). `start-api.sh` already had the self-locate block — only needed the bind fix. |
| cb-data-structure | Yes (uncommitted — see below) | Yes. Backend/CLI verified: `python3 -c "from api.app import app"`, `import batch_generate`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`digital-duck/cb-data-structure`) | Seventh repo done. No custom `api/config.py` validator (used base's file directly, like cb-data-science). Already had the language-suffix catalog fix independently; added the missing `model_seg` fix via direct `catalog_svc.py` copy. Missing spl3-self-locate `start-api.sh` fix (added it, plus bind change). Caught a real gap in the migration methodology here: `scripts/concept_graph.py` had picked up an XSS-safety fix (DOM-based tooltip construction instead of raw HTML string interpolation) during this base's own refactor that wasn't in the per-repo "always identical, direct copy" checklist — audited all prior repos (cb-college-physics through cb-algorithms) and confirmed each already had it correctly via the "IDENTICAL → copy base's current file" rule; only this repo's copy had been done before that file was updated. Worth double-checking this file specifically on `cb-graph-intro` and `cb-biology` too. |
| cb-biology | Yes (uncommitted — see below) | YES. Backend/CLI verified: `python3 -c "from api.app import app"`, `import batch_generate`, `spl3 validate`, `vite build` all pass clean. Frontend not yet exercised in a browser or against a live generate run. | Yes (`wgong/cb-biology` — different org than the rest) | Ninth standard-template repo done. Cleanest migration of the batch — every touched file was byte-identical to base's pre-refactor version, so the whole migration was direct copies of base's current files (no merges needed). One naming quirk: uses `.env.example` (matching this base's own filename) rather than the `example.env` name the other repos use — updated that file's Compare Cache section to the Direct adapter API keys block same as elsewhere. Confirm intended remote/ownership before pushing a migration branch. |
| cb-chemistry | YES.  | YES.  | Yes (`digital-duck/cb-chemistry`) | Tenth standard-template repo, not yet migrated. **Not the same repo as `cb-chemistry-ide`** — that's the separate derived app used to prototype this whole refactor (see Summary above) and already has the new Graph-IDE UI; `cb-chemistry` is independently seeded, still has the old split-page (`BookPage.js`/`ConceptPanel.js`/`BookViewer.js`) template shape, and has never been touched by this refactor. 21 domains, all citing OpenStax *Chemistry 2e* — no `source` field populated on any domain's `catalog.json` entry yet (same gap `cb-biology`/`cb-data-science` had before their About-page fix; add `source` + a "Content source" section on `About.js` with the companion-motivation paragraph as part of this repo's migration, using `https://openstax.org/details/books/chemistry-2e` as the URL — verify against the PDF's own front matter in `concept-book-press/input/chemistry-2e.pdf` first). Do not copy from `cb-chemistry-ide` — that app's own independent divergence hasn't been audited; migrate it the same mechanical way as the other 9. |

`is_valid` is left blank pending an actual pre-migration smoke test of each repo (dev
server boots, a known-generated page still renders) — fill in per-repo as each is
checked, rather than assumed.
