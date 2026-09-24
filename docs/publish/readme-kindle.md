# Publishing 元健康 Meta-Health on Amazon Kindle — plan and step-by-step guide

- **Created:** 2026-09-24
- **Status:** plan. Nothing submitted yet.
- **Audience:** a first-time author. Every step is spelled out.

> **Verify before you act.** Amazon changes KDP rules, royalty terms and file requirements from
> time to time. Everything below reflects KDP as of this writing. Where a detail matters (prices,
> fees, language support, AI-disclosure wording), check the current page in KDP's Help Center
> (kdp.amazon.com → Help) before relying on it. Items marked **(verify)** are the ones most
> likely to have changed.

---

## Part 1 — What we are publishing

### 1.1 Products

| Product | Format | Priority |
|---|---|---|
| **Meta-Health (English)**, Core level | Kindle eBook + paperback | **First.** Proves the whole pipeline. |
| **元健康 (Chinese)**, Core level | Kindle eBook + paperback | Second, after zh v2 passes evaluation (`docs/readme-todo.md`) |
| Intro-level edition (general readers) | eBook | Later. The same graphs regenerated with `--level intro`. |
| A short "10-Minute Daily Protocol" companion | eBook, cheap or free | Later. A lead magnet (see Part 4). |

**Start with one English eBook.** Publishing the first book teaches you the process. Everything
after that is repetition.

### 1.2 What the manuscript is made of

| Fact | Number |
|---|---|
| Chapters | 9 |
| Sections generated | 214 (per language) |
| **Unique** concepts | 168 |
| Duplicate sections | 46. Later chapters re-declare earlier concepts ("from Chapter N") as their own primitives, so those get a full section again. |
| English words (all 214 pages) | ~63,000 → **~50,000 after de-duplication** |
| Estimated paperback length | ~200–230 pages at 6″ × 9″ |

That is a normal nonfiction length. Health and self-help books are typically 40–70k words.

### 1.3 The book's structure (reading order)

The web app is non-linear: a graph you can click around in. A book is linear, so the manuscript
needs front and back matter around the nine chapters:

**Front matter**
1. Title page: *元健康 Meta-Health: Movement, Eating, and Mind as One Practice*
2. Copyright page (see Part 2.6), including the **health disclaimer** and an **AI-assistance statement**
3. Dedication (optional)
4. **Preface, in your own words, 2–4 pages.** Why you wrote this: years of daily 八段锦, the
   insight that eating is exercise for the internal organs, the conversation that grew into
   a framework. **This is the most important human-written part of the book.** It is what makes
   it *your* book, and readers buy authors, not topics.
5. How to read this book: the dual lens (TCM and physiology), what the concept graph is, and how
   to judge the evidence (from Ch2 and Ch9's evidence-and-safety material)

**Body:** Chapters 1–9, sections in teaching order (the order `book_{capstone}.html` uses), each
concept appearing **once**, in the chapter where it first appears. Where a later chapter reuses it,
add a one-line cross-reference ("see Chapter 5, *Eating as Internal Exercise*").

**Back matter**
1. **The Five-Phase integration table** (Ch9) as a one-page reference
2. **The daily Meta-Health protocol** as a one-page checklist
3. English ↔ Chinese glossary of the TCM terms (阴阳, 气, 五行, 脾主运化, …)
4. References and further reading (real, checked sources only)
5. About the author, plus a link to the free interactive web version (the GitHub Pages app)

---

## Part 2 — Getting the manuscript ready (the real work)

### 2.1 Editorial pass (you, not the LLM)

The generated text is a **draft**. Budget real time for this. It is what separates a good
book from the flood of AI-generated books on Amazon.

- [ ] Read every section. Fix anything wrong, awkward or repetitive. Check the practice problems.
- [ ] **Health-claims check:** no claim that anything *cures* or *treats* a disease; traditional
      claims labeled as traditional; evidence claims matched to real studies.
- [ ] **TCM accuracy check:** ideally ask a licensed TCM practitioner to read Ch1, Ch3, Ch4 and
      Ch6. Name them in the acknowledgments. It adds credibility.
- [ ] **Remove leftover formulas** that the zh v2 fix doesn't catch in English (see
      `docs/readme-todo.md`; the en rerun is still pending).
- [ ] **De-duplicate** the 46 repeated sections (see 2.3).
- [ ] Write the preface, the chapter introductions (one paragraph each, tying the chapter to the
      book's thread) and the conclusion.
- [ ] **Keep a log of your edits** (git commits are enough). It documents your human authorship
      (see 2.6).

### 2.2 Photos and illustrations

A movement book needs pictures. The five-organ exercises and the eight Baduanjin forms are hard
to follow from text alone.

- **Photograph yourself** doing each movement. There are 5 + 8 = 13 movements, with 2–3 photos
  each (start, peak, end). Use a phone, a plain background, even light and landscape orientation.
- Add simple diagrams: the generating and controlling cycles, the organ clock, and the balanced plate.
- Kindle eBook images: JPEG/PNG. Use at least 1000 px on the long side for photos, and keep
  file sizes modest, because file size affects the 70% royalty's delivery fee (see 3.4).

### 2.3 Assembly pipeline (to build)

The web app's per-concept HTML pages are the raw material. A new script,
**`scripts/build_book.py`** (not yet written), would:

1. **Order** the sections: chapter 1–9, each in its book's teaching order (from `setup_domain` /
   `book_{capstone}.html`).
2. **De-duplicate:** keep each concept at its first appearance, and replace later copies with a
   cross-reference line.
3. **Merge** in the front and back matter (Markdown files you write, e.g. `docs/publish/front/*.md`).
4. **Convert math:** Kindle can't run MathJax. Pre-render every `$…$` / `$$…$$` to **SVG or PNG
   images** (or MathML, **(verify)** how Kindle Previewer handles it). After the formula fixes
   there should be few, and the book is better with fewer.
5. **Output:**
   - **EPUB 3** for the Kindle eBook, via `pandoc` with a `metadata.yaml` (title, author,
     language, cover) and a small CSS file
   - **PDF** for the paperback interior, 6″ × 9″, fonts embedded, via the same HTML → PDF path
     `scripts/html2pdf.js` already uses, or WeasyPrint
6. **Validate:** run **EPUBCheck** (must pass with no errors) and preview in **Kindle Previewer 3**
   (a free Amazon app) on phone, tablet and e-reader layouts.

For the **Chinese** edition, embed a CJK font in the PDF (e.g. Noto Serif CJK SC; its license
allows embedding) and check the line breaking in Kindle Previewer.

I can build `scripts/build_book.py` when you're ready. It's a good next coding task.

### 2.4 Cover

- **Kindle eBook cover:** JPEG, ideally **2560 × 1600 px** (height × width, a 1.6:1 ratio) **(verify)**.
- **Paperback cover:** one PDF with back + spine + front. Spine width depends on page count and
  paper, so use KDP's cover calculator / template generator.
- Options: KDP's free **Cover Creator** (fine for a first book), a designer on Fiverr/99designs
  (about $50–300), or design it yourself in Canva.
- Design: the title in both scripts (元健康 / Meta-Health) is distinctive. It must stay readable
  as a **thumbnail**, because most shoppers see it at about 100 px wide.
- Don't use the Meta (Facebook) logo style or anything resembling a brand (see 4.5, trademarks).

### 2.5 Metadata: write this before you open KDP

| Field | Notes |
|---|---|
| Title / subtitle | *元健康 Meta-Health* / *Movement, Eating, and Mind as One Practice*. The subtitle is searchable, so make it say what the book is about. |
| Author | Your real name or a pen name. Pick one and keep it for every edition. |
| Description | 150–300 words. Lead with the reader's problem (fatigue, stress, digestion, too little time), then the 10-minute daily answer, then who you are. No cure claims. |
| Keywords | 7 slots, each a short phrase, e.g. *baduanjin qigong*, *mindful eating*, *traditional chinese medicine for beginners*, *five elements health*, *daily health routine*, *qigong for seniors*, *gut health exercise* |
| Categories | Choose up to 3 **(verify)**, e.g. Health & Fitness › Alternative Medicine › Chinese Medicine; Health & Fitness › Exercise › Qigong/Tai Chi; Health & Fitness › Diet & Nutrition |
| Language | English (the zh edition is its own product) |
| Age / audience | Adult |

### 2.6 Legal pages and required disclosures

- **Health disclaimer** (copyright page and the end of the introduction), e.g.:
  *"This book is for general education. It is not medical advice and does not replace
  diagnosis or treatment by a qualified professional. Consult your doctor before starting a new
  exercise or diet program, especially if you are pregnant, have a chronic condition such as
  diabetes or heart disease, or take medication."*
- **AI disclosure to Amazon:** KDP asks during setup whether the book contains
  **AI-generated** content (text, images or translations), as distinct from AI-*assisted* content
  that you wrote and only edited with AI help. The sections here were generated by an LLM
  from your concept graph and then edited by you, so **answer truthfully: AI-generated text, with
  human selection, structure and editing** **(verify the current form wording)**. Amazon doesn't
  show this answer to buyers, but a wrong answer can get the account suspended.
- **AI statement in the book (recommended):** a short, honest note on the copyright page or in
  the preface. For example: *"The structure of this book, a graph of 168 concepts, was designed by
  the author; the section drafts were generated with AI tools from that structure and then
  reviewed and edited by the author."* Honesty here is a selling point, not a weakness. It
  *is* the ConceptBook story.
- **Copyright:** under current US Copyright Office guidance, purely AI-generated text isn't
  copyrightable, but **human selection, arrangement and edits are**. Your concept graphs, the
  framework, the preface and your edits are your work. Keep the git history as evidence. (This is
  general information, not legal advice. If the business grows, ask an IP lawyer.)
- **Photos:** use only photos you took, or ones you have rights to.

---

## Part 3 — Publishing on KDP, step by step

### 3.1 Set up your account (one time, about 30 minutes)

1. Go to **kdp.amazon.com** and sign in with your Amazon account (or create a separate one for the business).
2. Complete **Account → Author/Publisher information**: legal name and address.
3. Complete the **Tax interview**. A US person submits a W-9 (SSN or an EIN; an EIN from the
   IRS is free and keeps your SSN off paperwork).
4. Add **bank details** for royalty payments. Amazon pays about 60 days after the end of each month.

### 3.2 Create the eBook (Bookshelf → "+ Create" → Kindle eBook)

**Page 1: Kindle eBook Details**
- Language, title, subtitle, series (optional; could be "Meta-Health Series" for later editions),
  edition number, author, contributors (e.g. a TCM reviewer)
- Description, publishing rights ("I own the copyright…"), keywords, categories, age range
- Pre-order: skip it for the first book

**Page 2: Kindle eBook Content**
- **Manuscript:** upload the **EPUB** (DOCX and KPF are also accepted; MOBI is no longer
  accepted for reflowable eBooks) **(verify)**
- DRM: your choice (it makes little practical difference)
- **Cover:** upload your JPEG (or use Cover Creator)
- **AI-generated content** question: answer as described in 2.6
- **Preview:** always open the online previewer and page through every chapter
- ISBN: **not needed** for a Kindle eBook (Amazon assigns an ASIN)

**Page 3: Kindle eBook Pricing**
- **KDP Select** (optional, 90 days, renewable): the eBook must be **exclusive to Amazon** in
  digital form, but it enters **Kindle Unlimited** (you're paid per page read) and gets promo
  tools (5 free days or Countdown Deals per 90 days). Good for a first book with no audience.
  You can leave after 90 days.
- **Territories:** worldwide.
- **Royalty:**
  - **70%** if the list price is **$2.99–$9.99** in the main markets, minus a small delivery fee
    based on file size (a few cents per MB) **(verify)**
  - **35%** otherwise
- **Suggested price:** **$4.99–$6.99**. At $5.99 × 70% you earn about $4 per sale.
- Click **Publish**. Review usually takes up to 72 hours. You'll get an email when it's live.

### 3.3 Create the paperback (Bookshelf → "+ Create" → Paperback)

- Same details as the eBook (link them, so both appear on one product page).
- **ISBN:** take KDP's **free ISBN** (the imprint shows "Independently published"), or buy your
  own if you want your own imprint name. (US ISBNs come only from Bowker; one ISBN costs about
  $125, and a block of 10 is much cheaper per ISBN.) **(verify)**
- **Print options:** black-and-white interior (color costs much more; photos are fine in B&W
  if they are well lit), cream or white paper, **6″ × 9″**, no bleed (unless images run to the
  page edge), matte or glossy cover.
- Upload the interior **PDF** and the cover **PDF** (or use Cover Creator). Use the **online
  previewer**: it flags text in the margins, low-resolution images and similar problems.
- **Order a printed proof copy** (at print cost plus shipping) and read it on paper. You will
  find mistakes you missed on screen.
- **Pricing:** paperback royalty is 60% of list price minus the printing cost. The printing cost
  for about 220 pages is roughly $3.50–4.50 **(verify in KDP's calculator)**. At $14.99 you'd earn
  about $4.50–5.50 per copy.

### 3.4 After you publish

- **Author Central** (author.amazon.com): claim your book, add a bio and photo, and link both editions.
- **A+ Content** (from KDP's Marketing page): add images and comparison modules to the product
  page. Photos of the movements work well here.
- **Reviews:** give advance copies to 10–20 practitioners or friends and ask them to post honest
  reviews after launch. Never pay for reviews or swap reviews; Amazon removes them and can
  penalize the account.
- **Reports:** KDP Reports shows sales and KENP page reads daily.

### 3.5 The Chinese edition

- **Kindle language support (verify):** check KDP's "supported languages" page to see whether
  Chinese is accepted for eBooks and paperbacks, and in which script (Simplified or Traditional).
- **Kindle China closed its store (2023–2024)**, so Amazon reaches mainly overseas Chinese readers.
  For mainland readers, consider **微信读书**, **豆瓣阅读**, **Apple Books** and **Google Play
  Books**. A KDP Select exclusivity period would block those for the eBook, so don't enroll the
  zh eBook in Select if you plan to use them.
- Keep the glossary and the author's preface consistent across both editions.

---

## Part 4 — Taking the research to business level

### 4.1 Know what you actually own

You have **three separate assets**, and they are different businesses:

| Asset | What it is | Business model |
|---|---|---|
| **A. The Meta-Health framework** (内调一元论) | An original synthesis: eating as internal exercise, 五脏操 ↔ 八段锦, Five-Phase daily protocol | Content and education brand: books, courses, workshops, coaching |
| **B. ConceptBook** (graph → multi-level, multi-language book pipeline) | The technology: concept graphs + SPL + verifiers + web app | B2B service / platform for publishers, educators, schools |
| **C. You, the practitioner-author** | Years of daily practice, bilingual, technical | Credibility that makes A and B believable |

**My recommendation:** use **A as the proving ground for B**. One real, published, well-reviewed
book made with ConceptBook is worth more to publishers, and to the paper's reviewers, than any
demo. Put most of your effort into B over time, because technology scales and personal
teaching doesn't. A alone is a good *side* business; B is the one that could become a company.

### 4.2 Stage 1 (months 0–3): publish and build an audience

- Publish the English eBook and paperback (Parts 2–3).
- **Keep the free web app public** and link it from the book. The interactive graph is a
  differentiator no other health book has.
- **Start an email list** (Buttondown, Substack or ConvertKit). Offer the **one-page daily protocol
  and Five-Phase table as a free PDF** in exchange for an email address. The list is the most
  valuable thing you'll build; Amazon owns its customers, but the list is yours.
- **Short videos:** a 10-minute 五脏操 / 八段锦 routine on YouTube, plus shorter clips for 小红书
  and WeChat Channels (视频号) for Chinese audiences. The movement *is* the content, and it
  sells the book.
- Measure: sales per week, list sign-ups per week, video views. Only move to Stage 2 when some
  of these are growing.

### 4.3 Stage 2 (months 3–9): products people pay more for

In order of effort:
1. **Practice cards / poster:** the Five-Phase matrix and the daily protocol, printed (print-on-demand).
2. **Online course, "10 Minutes a Day: Meta-Health"** (Teachable, Thinkific, or YouTube
   memberships): video lessons that follow the chapters, with a 30-day practice challenge.
   $49–149.
3. **Workshops:** community centers, senior centers, libraries, Chinese community
   associations, and **corporate wellness** programs (companies pay for employee-wellness
   sessions). A 90-minute workshop, "Eating and Movement as One Practice".
4. **Train-the-trainer:** certify others to teach the protocol. This scales the in-person side.

### 4.4 Stage 3 (months 6–18): research credibility

A health brand is only as strong as its evidence. You're well placed to create some:
- **A small pilot study:** e.g. 20–40 volunteers doing the daily protocol for 8 weeks, measuring
  **HRV** (wearables), **post-meal glucose** (a continuous glucose monitor), sleep, and
  validated questionnaires (e.g. perceived stress, GI symptoms). Partner with a **university
  public-health or TCM department**; they provide ethics review (IRB) and statistics, you provide
  the protocol and the software. Pre-register the study.
- Publish the results, even if they're modest. It's an honest story either way, and it's rare in this space.
- The ConceptBook paper can cite the book as a **case study** of graph-first generation in a
  non-STEM, bilingual domain, including the formula-fabrication finding and the v1/v2 evaluation.

### 4.5 Protect yourself

- **Trademark search before branding:** check whether "Meta-Health" / "元健康" is registered in
  the relevant classes (books, education, health apps). Use the USPTO trademark search (and
  China's CNIPA if you'll sell in China). **Meta Platforms defends "Meta" aggressively**, so
  "Meta-Health" in apps or software could draw attention, while a book title is lower risk. A
  one-hour consultation with a trademark attorney before you invest in a logo, a domain or an
  app is cheap insurance.
- **Health-claim rules (US):** market as **wellness and education**, never as treatment. The FTC
  requires evidence for health claims in advertising; disease claims ("lowers blood sugar in
  diabetics", "cures insomnia") bring regulatory risk. The same care applies on Chinese platforms.
- **Business structure:** once there's revenue, form an **LLC** and get an EIN (for KDP taxes,
  bank account and contracts). Get liability insurance before running in-person classes.
- **Keep the author voice human:** readers and Amazon are increasingly skeptical of AI-generated
  books. Your practice, your photos, your preface and your honest AI statement are the answer.

### 4.6 ConceptBook as the bigger business (Asset B)

- **Offer:** "We turn your textbook, course or corpus into an interactive, multi-level,
  bilingual concept book in weeks, with a verifiable structure."
- **First customers:** OER / open-textbook groups (you're already republishing OpenStax),
  independent course creators, TCM and language schools, and corporate training teams.
- **Pricing models:** per-book setup fee plus hosting, or licensing the pipeline.
- **Proof points:** the published Meta-Health book (sales and reviews), the paper, the
  cb-* demo books (calculus, physics, history), and the v1/v2 quality evaluation, which shows you
  measure and fix LLM failure modes.
- **Validate before building:** talk to 10 potential customers before writing more platform
  code. Ask what they'd pay for and what they'd need to trust the output.

---

## Part 5 — Timeline and checklist

| Week | Milestone |
|---|---|
| 1 | zh v2 evaluated; decide on the en rerun; start writing the preface |
| 1–2 | Build `scripts/build_book.py` (ordering, de-duplication, math → images, EPUB/PDF) |
| 2–4 | Editorial pass on the English text (the largest task); photograph the 13 movements |
| 3 | Cover (Cover Creator or a designer); metadata written |
| 4 | KDP account, tax and bank setup; EPUBCheck + Kindle Previewer pass |
| 5 | **Publish the English eBook**; set up the paperback and order a proof |
| 6 | Proof corrections → **publish the paperback**; Author Central, A+ Content |
| 6–8 | Email list and free PDF; first videos; ask advance readers for reviews |
| 8–12 | Chinese edition (editing + channels); decide on Stage 2 products |

**Launch checklist**
- [ ] Manuscript edited, de-duplicated, fact-checked (health and TCM)
- [ ] Preface, chapter introductions and conclusion written by you
- [ ] Disclaimer and AI statement on the copyright page
- [ ] Photos and diagrams in place
- [ ] EPUB passes EPUBCheck; looks right in Kindle Previewer (phone, tablet, e-reader)
- [ ] Paperback PDF passes KDP's previewer; proof copy read on paper
- [ ] Cover readable as a thumbnail
- [ ] Metadata: title, subtitle, description, 7 keywords, categories
- [ ] KDP account: tax interview and bank details complete
- [ ] AI-content question answered truthfully
- [ ] Trademark search done for "元健康 Meta-Health"
- [ ] Free web version linked from the book; email sign-up ready
