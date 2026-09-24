#!/usr/bin/env python3
"""Count known content-quality problems in generated concept pages, per chapter.

Written to measure the 2026-09-24 prompt/style fixes (see docs/readme-todo.md):
compare an archived variant (e.g. the first zh run) with a regenerated one.

Metrics (page body only, so the MathJax config in <head> isn't counted):
  pages     concept_*.html pages found
  display   display equations ($$...$$)
  inline    inline math ($...$)
  broken    display equations that look malformed (unbalanced braces, or a
            '}}{' fraction tail with no \\frac)
  ids       snake_case identifiers leaking into the prose
  metabolic '代谢健康' / 'metabolic health' in a book_*.html payoff
            (the meta → metabolic mistranslation)

Usage:
  python scripts/eval_generated_content.py                              # live core.zh + core.en
  python scripts/eval_generated_content.py --dir v1=archive/zh-v1 --dir v2=public/domains
"""
import html
import re
from pathlib import Path

import click

REPO = Path(__file__).resolve().parent.parent
DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE = re.compile(r"(?<![\$\\])\$(?!\$)([^$\n]+?)(?<!\\)\$(?!\$)")
SNAKE = re.compile(r"\b[a-z]{2,}(?:_[a-z]{2,})+\b")  # node ids, not LaTeX subscripts like theta_i
TAG = re.compile(r"<[^>]+>")


def _body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("<body", 1)[-1]


def _chapter_stats(html_dir: Path) -> dict:
    s = dict(pages=0, display=0, inline=0, broken=0, ids=0, metabolic=0)
    for page in sorted(html_dir.glob("concept_*.html")):
        body = _body(page)
        s["pages"] += 1
        blocks = DISPLAY.findall(body)
        s["display"] += len(blocks)
        s["inline"] += len(INLINE.findall(DISPLAY.sub("", body)))
        s["broken"] += sum(1 for b in blocks
                           if b.count("{") != b.count("}") or ("}}{" in b and "\\frac" not in b))
        prose = html.unescape(TAG.sub(" ", INLINE.sub(" ", DISPLAY.sub(" ", body))))
        s["ids"] += len(SNAKE.findall(prose))
    for book in html_dir.glob("book_*.html"):
        prose = html.unescape(TAG.sub(" ", _body(book)))
        s["metabolic"] += prose.count("代谢健康") + prose.lower().count("metabolic health")
    return s


def _find_html_dirs(root: Path, variant: str) -> dict[str, Path]:
    """Map chapter id -> html dir, for either public/domains or an archive dir.

    public/domains/<ch>/output/<variant>/<model>/html  or  <archive>/<ch>/<model>/html
    """
    found = {}
    for d in sorted(root.glob(f"meta_health_ch*/output/{variant}/*/html")):
        found[d.parts[-5]] = d
    for d in sorted(root.glob("meta_health_ch*/*/html")):
        found.setdefault(d.parts[-3], d)
    return found


@click.command()
@click.option("--dir", "dirs", multiple=True,
              help="LABEL=PATH to compare; PATH is public/domains or an archive dir. "
                   "Default: live core.en and core.zh.")
@click.option("--variant", default="core.zh", show_default=True,
              help="Output variant to read under public/domains.")
def main(dirs: tuple[str, ...], variant: str) -> None:
    if dirs:
        runs = [(lbl, REPO / p, variant) for lbl, p in (d.split("=", 1) for d in dirs)]
    else:
        runs = [("en", REPO / "public/domains", "core.en"), ("zh", REPO / "public/domains", "core.zh")]

    cols = ("pages", "display", "inline", "broken", "ids", "metabolic")
    for label, root, var in runs:
        chapters = _find_html_dirs(root, var)
        click.echo(f"\n[{label}]  {root}  ({var})")
        click.echo(f"  {'chapter':18s}" + "".join(f"{c:>10s}" for c in cols))
        total = dict.fromkeys(cols, 0)
        for ch, d in chapters.items():
            st = _chapter_stats(d)
            for c in cols:
                total[c] += st[c]
            click.echo(f"  {ch:18s}" + "".join(f"{st[c]:>10d}" for c in cols))
        click.echo(f"  {'TOTAL':18s}" + "".join(f"{total[c]:>10d}" for c in cols))


if __name__ == "__main__":
    main()
