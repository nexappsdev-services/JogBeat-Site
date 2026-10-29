#!/usr/bin/env python3
"""Builds the static Jogbeat site (landing, support, privacy × 4 languages) for GitHub Pages.
Usage: build.py <src dir with privacy.<lang>.md + icon-1024.png> <out dir>"""
import html, os, re, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import EMAIL, LANGS, LANG_NAME, HTML_LANG, T

SRC, OUT = sys.argv[1], sys.argv[2]
EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"&lt;(https?://[^&\s]+)&gt;", r'<a href="\1">\1</a>', s)
    s = re.sub(r"(?<![\w.:/\"])([\w.+-]+@[\w-]+\.[\w.]+)", r'<a href="mailto:\1">\1</a>', s)
    return s

def md_to_html(md):
    """Just enough Markdown for the policy files: headings, paragraphs, lists, tables, rules, bold, autolinks."""
    out, para, lines = [], [], md.strip().splitlines()
    def flush():
        if para: out.append("<p>" + "<br>".join(inline(l) for l in para) + "</p>"); para.clear()
    i = 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip(): flush(); i += 1; continue
        if l.startswith("# "): flush(); i += 1; continue  # the page title comes from the template
        m = re.match(r"## (\d+)\.\s*(.*)", l)
        if m: flush(); out.append(f'<h2 id="s{m.group(1)}">{m.group(1)}. {inline(m.group(2))}</h2>'); i += 1; continue
        if l.startswith("## "): flush(); out.append(f"<h2>{inline(l[3:])}</h2>"); i += 1; continue
        if l.strip() == "---": flush(); out.append("<hr>"); i += 1; continue
        if l.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = ['<div class="table"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            t += ["<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body]
            out.append("".join(t) + "</tbody></table></div>"); continue
        if l.startswith("- "):
            flush(); items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
        para.append(l.strip()); i += 1
    flush()
    return "\n".join(out)

CSS = """:root{--brand:#FF7A1A;--brand-text:#B84A08;--bg:#FFFBF7;--card:#FFFFFF;--text:#1F1A16;--muted:#6B6158;--line:#EFE4DA;--tint:#FFF0E3}
@media (prefers-color-scheme:dark){:root{--brand-text:#FF9F4A;--bg:#141110;--card:#1F1B19;--text:#F4EEE9;--muted:#B3A79D;--line:#3A322D;--tint:#2B211A}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang TC","PingFang SC","Hiragino Sans","Noto Sans CJK TC",sans-serif}
a{color:var(--brand-text)}
.wrap{max-width:760px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--line);background:var(--card)}
.bar{display:flex;align-items:center;gap:12px;min-height:60px;flex-wrap:wrap;padding:8px 0}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;text-decoration:none;color:var(--text);margin-right:auto}
.brand img{width:32px;height:32px;border-radius:8px}
nav a{text-decoration:none;color:var(--muted);margin-left:14px;font-size:15px}nav a[aria-current]{color:var(--brand-text);font-weight:600}
.langs{font-size:14px;color:var(--muted);padding:6px 0 0}.langs a{margin-right:12px;text-decoration:none}.langs a[aria-current]{font-weight:700}
main{padding:28px 0 48px}h1{font-size:30px;line-height:1.3;margin:8px 0 4px}h2{font-size:21px;margin:36px 0 10px;scroll-margin-top:16px}
.meta{color:var(--muted);font-size:15px}
.hero{text-align:center;padding:24px 0 8px}.hero img{width:112px;height:112px;border-radius:25px;box-shadow:0 8px 24px rgba(0,0,0,.12)}
.hero p.lead{font-size:19px;color:var(--muted);max-width:520px;margin:12px auto}
.badge{display:inline-block;margin-top:8px;padding:10px 18px;border-radius:12px;background:var(--tint);color:var(--brand-text);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin:28px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}.card h3{margin:0 0 4px;font-size:17px}.card p{margin:0;color:var(--muted);font-size:15px}
.links{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:8px}.links a{padding:10px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);text-decoration:none}
details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:10px 0}summary{cursor:pointer;font-weight:600}details p{margin:10px 0 2px}
.contact{background:var(--tint);border-radius:14px;padding:16px 18px}
.table{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border:1px solid var(--line);padding:8px 10px;vertical-align:top;text-align:left}th{background:var(--tint)}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:14px;padding:20px 0 40px}footer a{color:var(--muted)}
"""

def page(lang, kind, title, body, depth):
    t = T[lang]; up = "../" * depth
    def href(l, k): return f"{up}{l}/" + ("" if k == "home" else f"{k}/")
    nav = "".join(f'<a href="{href(lang, k)}"{" aria-current=page" if k == kind else ""}>{t["nav_" + k]}</a>' for k in ["support", "privacy"])
    langs = "".join(f'<a href="{href(l, kind)}" hreflang="{HTML_LANG[l]}"{" aria-current=true" if l == lang else ""}>{LANG_NAME[l]}</a>' for l in LANGS)
    alt = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{href(l, kind)}">' for l in LANGS)
    return f"""<!doctype html>
<html lang="{HTML_LANG[lang]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(t['hero'])}">
<link rel="icon" href="{up}assets/icon-64.png"><link rel="apple-touch-icon" href="{up}assets/icon-180.png"><link rel="stylesheet" href="{up}assets/style.css">{alt}</head>
<body><header><div class="wrap"><div class="bar"><a class="brand" href="{href(lang, 'home')}"><img src="{up}assets/icon-64.png" alt="">{t['app']}</a><nav>{nav}</nav></div>
<div class="langs" aria-label="{t['lang_label']}">{langs}</div></div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap"><p>{t['disclaimer']}</p><p><a href="{href(lang, 'support')}">{t['nav_support']}</a> · <a href="{href(lang, 'privacy')}">{t['nav_privacy']}</a> · <a href="{EULA}">{t['terms']}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></p><p>© 2026 Nex</p></div></footer>
</body></html>
"""

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)

def redirect(target_kind, depth):
    """Picks the visitor's language; without JavaScript it is a plain list of links."""
    up = "../" * depth; suffix = "" if target_kind == "home" else f"{target_kind}/"
    links = "".join(f'<li><a href="{up}{l}/{suffix}">{LANG_NAME[l]}</a></li>' for l in LANGS)
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>跑拍 Jogbeat</title>
<link rel="stylesheet" href="{up}assets/style.css"><script>
(function(){{var n=(navigator.languages&&navigator.languages[0]||navigator.language||'en').toLowerCase(),l='en';
if(/^zh-(hans|cn|sg|my)/.test(n))l='zh-Hans';else if(/^zh/.test(n))l='zh-Hant';else if(/^ja/.test(n))l='ja';
location.replace('{up}'+l+'/{suffix}'+location.hash);}})();</script></head>
<body><main><div class="wrap"><h1>跑拍 Jogbeat</h1><ul>{links}</ul></div></main></body></html>
"""

shutil.rmtree(OUT, ignore_errors=True); os.makedirs(f"{OUT}/assets")
write(f"{OUT}/assets/style.css", CSS)
for size in (64, 180, 256):
    subprocess.run(["sips", "-Z", str(size), f"{SRC}/icon-1024.png", "--out", f"{OUT}/assets/icon-{size}.png"], check=True, capture_output=True)
open(f"{OUT}/.nojekyll", "w").close()
write(f"{OUT}/index.html", redirect("home", 0))
write(f"{OUT}/privacy/index.html", redirect("privacy", 1))
write(f"{OUT}/support/index.html", redirect("support", 1))
write(f"{OUT}/404.html", '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>404 · 跑拍 Jogbeat</title><link rel="stylesheet" href="/JogBeat-Site/assets/style.css"></head><body><main><div class="wrap"><h1>404</h1><p><a href="/JogBeat-Site/">跑拍 Jogbeat</a></p></div></main></body></html>')

for lang in LANGS:
    t = T[lang]
    feats = "".join(f'<div class="card"><h3>{h}</h3><p>{p}</p></div>' for h, p in t["features"])
    home = f"""<section class="hero"><img src="../assets/icon-256.png" alt="{t['app']}"><h1>{t['app']}</h1><p class="meta">{t['tagline']}</p>
<p class="lead">{t['hero']}</p><span class="badge">{t['soon']}</span></section><div class="grid">{feats}</div>
<div class="links"><a href="support/">{t['nav_support']}</a><a href="privacy/">{t['nav_privacy']}</a></div>"""
    write(f"{OUT}/{lang}/index.html", page(lang, "home", f"{t['app']} — {t['tagline']}", home, 1))

    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in t["faq"])
    support = f"""<h1>{t['support_title']}</h1><p class="meta">{t['app']} · {t['tagline']}</p><p>{t['support_intro']}</p>
<section class="contact" id="contact"><h2 style="margin-top:0">{t['contact_title']}</h2><p>{t['contact_body'].format(e=EMAIL)}</p><p class="meta">{t['contact_tip']}</p></section>
<h2 id="faq">{t['faq_title']}</h2>{faq}
<h2 id="terms">{t['terms']}</h2><p>{t['terms_note']} <a href="{EULA}">{EULA}</a></p>"""
    write(f"{OUT}/{lang}/support/index.html", page(lang, "support", f"{t['support_title']} — {t['app']}", support, 2))

    md = open(f"{SRC}/privacy.{lang}.md", encoding="utf-8").read()
    title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    write(f"{OUT}/{lang}/privacy/index.html", page(lang, "privacy", title, f"<h1>{inline(title)}</h1>\n" + md_to_html(md), 2))
print("built", OUT)
