"""Mark question packs as free or members-only across the site.

Run from the repository root:  python3 tools/lock_packs.py

Rule: the first topic of each course is free; every other topic is members only.
- assets/packs.json gets "free": true/false on every topic. Locked topics keep their
  file names under "file" but lose the public "q"/"a" links.
- Each course page shows download links for the free topic and a "Members only"
  button for the rest.
Members-only PDFs are NOT kept in this public repository. They live in the private
repository mathstutoruk/mathstutor-packs (and, once accounts are live, in a private
Supabase storage bucket served only to signed-in members).
"""
import json
import re

PACKS = "assets/packs.json"

LOCK_HTML = ('<div class="pack-downloads pack-locked">\n'
             '              <a class="btn-members" href="login.html?next=packs" aria-label="Members only: log in to download {title}">Members only</a>\n'
             '            </div>')


def slug_of(path):
    return re.sub(r"-(questions|answers)\.pdf$", "", path.split("/")[-1])


def main():
    data = json.load(open(PACKS, encoding="utf-8"))
    for page, course in data.items():
        first = True
        locked_slugs = set()
        for sec in course["sections"]:
            for t in sec["topics"]:
                if "file" not in t:
                    t["file"] = slug_of(t.get("q") or t.get("a"))
                t["free"] = first
                if first:
                    t["q"] = f"packs/{t['file']}-questions.pdf"
                    t["a"] = f"packs/{t['file']}-answers.pdf"
                else:
                    t.pop("q", None)
                    t.pop("a", None)
                    locked_slugs.add(t["file"])
                first = False
        path = page + ".html"
        html = open(path, encoding="utf-8").read()

        def repl(m):
            block = m.group(0)
            s = re.search(r'href="packs/([^"]+)-questions\.pdf"', block)
            if not s or s.group(1) not in locked_slugs:
                return block
            title = re.search(r"<h3>(.*?)</h3>", block).group(1)
            return re.sub(r'<div class="pack-downloads">.*?</div>', LOCK_HTML.replace("{title}", title), block, flags=re.S)

        html = re.sub(r"<li>\s*<div>\s*<h3>.*?</li>", repl, html, flags=re.S)
        open(path, "w", encoding="utf-8").write(html)
    json.dump(data, open(PACKS, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
