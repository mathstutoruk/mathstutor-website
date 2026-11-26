"""Rebuild every page of mathstutor.co.uk in the shared Style A shell.

Run from the repository root:  python3 tools/build_pages.py
Keeps each page's own <main> content, title and description; replaces the
old header, footer, fonts and stylesheets with the shared ones in assets/.
"""
import glob
import html
import re

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n'
         '<link rel="stylesheet" href="assets/site.css">\n'
         '<link rel="icon" href="images/home/logo.webp" type="image/webp">')

NAV = [("index.html#lessons", "Lessons", "lessons"),
       ("group-classes.html", "Group classes", "group"),
       ("question-packs.html", "Question packs", "packs"),
       ("articles.html", "Articles", "articles"),
       ("bio.html", "About", "about")]

BURGER = ('<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor" aria-hidden="true">'
          '<path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>')


def header(active):
    def links():
        out = []
        for href, label, key in NAV:
            cur = ' aria-current="page"' if key == active else ''
            out.append(f'<a href="{href}"{cur}>{label}</a>')
        return out
    cur = ' aria-current="page"' if active == "contact" else ''
    return f'''<a class="skip" href="#mainContent">Skip to content</a>
<header class="head">
  <div class="wrap head-row">
    <a class="brand" href="index.html"><img src="images/home/logo.webp" alt="" width="48" height="48">maths<b>tutor</b></a>
    <nav class="nav" aria-label="Main">
      {chr(10).join("      " + l for l in links()).strip()}
      <a class="btn btn-gold" href="contact.html"{cur}>Get in touch</a>
    </nav>
    <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="mnav">{BURGER}</button>
  </div>
  <nav class="wrap mnav" id="mnav" aria-label="Mobile">
    {"".join(links())}
    <a class="btn btn-gold" href="contact.html">Get in touch</a>
  </nav>
</header>'''


FOOTER = '''<footer class="foot">
  <div class="wrap">
    <div class="fg">
      <div><a class="brand" href="index.html"><img src="images/home/logo.webp" alt="" width="48" height="48">maths<b>tutor</b></a><p>GCSE and A-level Maths tuition with Surinder Sangha. Online and in Notting Hill.</p></div>
      <div><h4>Lessons</h4><ul><li><a href="contact.html">One-to-one</a></li><li><a href="group-classes.html">Group classes</a></li><li><a href="contact.html">Book a lesson</a></li></ul></div>
      <div><h4>Resources</h4><ul><li><a href="question-packs.html">Question packs</a></li><li><a href="articles.html">Articles</a></li><li><a href="maths-revision-plan.html">Revision plan</a></li></ul></div>
      <div><h4>About</h4><ul><li><a href="bio.html">About me</a></li><li><a href="contact.html">Contact</a></li></ul></div>
    </div>
    <div class="legal"><span>Maths Tutor Limited. Registered in England and Wales, company number 17469182.</span><span>© Maths Tutor Limited 2026</span></div>
  </div>
</footer>
<script src="assets/site.js" defer></script>'''


def head_meta(src):
    head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
    keep = []
    for pat in [r"<title>.*?</title>", r'<meta\s+name="description".*?>', r'<link rel="canonical".*?>',
                r'<meta property="og:.*?>', r'<script type="application/ld\+json">.*?</script>']:
        keep += re.findall(pat, head, re.S)
    return "\n".join(k.strip() for k in keep)


def page(meta, active, main, extra_script=""):
    return f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{meta}
{FONTS}
</head>
<body class="page">
{header(active)}
{main}
{FOOTER}
{extra_script}
</body>
</html>
'''


def active_for(name):
    if name == "group-classes.html":
        return "group"
    if name == "question-packs.html" or name.endswith("-question-packs.html"):
        return "packs"
    if name == "bio.html":
        return "about"
    if name == "contact.html":
        return "contact"
    return "articles"


def tidy_main(name, main):
    main = main.replace('id="mainContent" tabindex="-1"', 'id="mainContent"')
    if 'id="mainContent"' not in main:
        main = main.replace("<main", '<main id="mainContent"', 1)
    # Breadcrumbs: articles start at Home; give pack pages the same.
    main = main.replace('<li><a href="question-packs.html">Question Packs</a></li>',
                        '<li><a href="index.html">Home</a></li><li><a href="question-packs.html">Question packs</a></li>')
    main = main.replace("<span>Maths Tutor UK</span>", "<span>Surinder Sangha</span>")
    if name == "articles.html":
        main = main.replace('<span class="eyebrow">GCSE &amp; A-Level Mathematics</span>', "")
    if name == "bio.html":
        main = main.replace('<main class="container">', '<main id="mainContent" class="container">')
    return main


CONTACT_MAIN = '''<main id="mainContent" class="contact-hero">
  <div class="wrap contact-grid">
    <section>
      <h1 class="contact-title">Book your first lesson</h1>
      <p class="contact-lede">Tell me about the student and what they need help with. I'll reply by email with availability.</p>
      <form class="form-card" action="https://formspree.io/f/mpqbqbww" method="POST">
        <input type="hidden" name="_subject" value="New enquiry from mathstutor.co.uk">
        <input type="hidden" name="_captcha" value="false">
        <div class="form-row">
          <div class="form-group"><label for="firstName">First name</label><input id="firstName" type="text" name="first_name" autocomplete="given-name" required></div>
          <div class="form-group"><label for="lastName">Last name</label><input id="lastName" type="text" name="last_name" autocomplete="family-name" required></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label for="email">Email</label><input id="email" type="email" name="email" autocomplete="email" required></div>
          <div class="form-group"><label for="phone">Phone <span>(optional)</span></label><input id="phone" type="tel" name="phone" autocomplete="tel"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label for="tuitionSubject">Subject</label>
            <select id="tuitionSubject" name="tuition_required">
              <option value="GCSE Mathematics">GCSE Maths</option>
              <option value="GCSE Further Mathematics">GCSE Further Maths</option>
              <option value="A-Level Mathematics">A-level Maths</option>
              <option value="Further Mathematics">A-level Further Maths</option>
            </select></div>
          <div class="form-group"><label for="tuitionFormat">Lesson type</label>
            <select id="tuitionFormat" name="tuition_format">
              <option value="">Choose one</option>
              <option value="One-to-one">One-to-one lessons</option>
              <option value="Group classes">Group classes</option>
            </select></div>
        </div>
        <div class="form-group"><label for="message">About the student</label>
          <textarea id="message" name="message" placeholder="Year group, exam board, current level and what they'd like help with."></textarea></div>
        <button type="submit" class="submit-btn">Send enquiry</button>
        <p class="form-note">I usually reply by email. Your details are only used to answer your enquiry.</p>
      </form>
    </section>
    <aside class="contact-side">
      <div class="side-card navy">
        <h2>Prices</h2>
        <ul class="ticks" style="grid-template-columns:1fr;margin:0">
          <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>One-to-one: £60 per hour</li>
          <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>Group classes: £30 per student per hour</li>
        </ul>
      </div>
      <div class="side-card faq">
        <h2>Questions</h2>
        <details><summary>Which subjects do you teach?</summary><p>GCSE Maths, GCSE Further Maths, A-level Maths and A-level Further Maths, for AQA, Edexcel, OCR and OCR MEI.</p></details>
        <details><summary>Online or in person?</summary><p>Online on Zoom anywhere in the UK, or in person in Notting Hill, subject to availability.</p></details>
        <details><summary>When are you available?</summary><p>Please enquire for availability and I'll reply with current times.</p></details>
        <details><summary>How do group classes work?</summary><p>Small online classes at £30 per student per hour. <a href="group-classes.html">See group classes</a>.</p></details>
        <details><summary>Do you have a DBS certificate?</summary><p>Yes, an enhanced DBS certificate is available on request.</p></details>
      </div>
    </aside>
  </div>
</main>'''

CONTACT_JS = '''<script>
{
  const q = new URLSearchParams(location.search);
  const subjects = {"gcse-maths": "GCSE Mathematics", "gcse-further-maths": "GCSE Further Mathematics",
                    "a-level-maths": "A-Level Mathematics", "a-level-further-maths": "Further Mathematics"};
  if (subjects[q.get("subject")]) document.getElementById("tuitionSubject").value = subjects[q.get("subject")];
  if (q.get("format") === "group") document.getElementById("tuitionFormat").value = "Group classes";
  if (q.get("format") === "one-to-one") document.getElementById("tuitionFormat").value = "One-to-one";
}
</script>'''


def build_inner():
    names = sorted(set(glob.glob("*.html")) - {"index.html", "preview-a.html", "preview-b.html"})
    for name in names:
        src = open(name, encoding="utf-8").read()
        if 'class="page"' in src:
            print("already built", name)
            continue
        meta = head_meta(src)
        meta = meta.replace(" | mathstutor.co.uk</title>", " | mathstutor.co.uk</title>")
        if name == "contact.html":
            out = page(meta, "contact", CONTACT_MAIN, CONTACT_JS)
        else:
            main = re.search(r"<main.*?</main>", src, re.S).group(0)
            out = page(meta, active_for(name), tidy_main(name, main))
        open(name, "w", encoding="utf-8").write(out)
        print("built", name)


def build_home():
    src = open("preview-a.html", encoding="utf-8").read()
    src = re.sub(r'<div class="switch">.*?</div>\n', "", src, flags=re.S)
    src = re.sub(r"<link rel=\"preconnect\".*?</style>\n", FONTS + "\n", src, flags=re.S)
    src = src.replace('<link rel="icon" href="images/home/logo.webp" type="image/webp">\n' + FONTS, FONTS)
    src = src.replace("<title>Style A: Maths hub | mathstutor.co.uk</title>",
                      "<title>GCSE &amp; A-level Maths Tutor | Surinder Sangha | mathstutor.co.uk</title>")
    src = src.replace('<a class="brand" href="#top">', '<a class="brand" href="index.html">')
    src = src.replace("<body>", '<body>\n<a class="skip" href="#top">Skip to content</a>', 1)
    open("index.html", "w", encoding="utf-8").write(src)
    print("built index.html")


if __name__ == "__main__":
    # index.html is now edited directly; build_home() was a one-off conversion.
    build_inner()
