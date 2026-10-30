#!/usr/bin/env python3
"""Builds the static Jogbeat site (landing, support, privacy × 4 languages) for GitHub Pages.
Usage: build.py <src dir with privacy.<lang>.md + icon-1024.png> <out dir>"""
import html, os, re, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import EMAIL, LANGS, LANG_NAME, HTML_LANG, T, APP_STORE_ID, FAQ_IDS, SHOTS, FEATURE_ART
HERE = os.path.dirname(os.path.abspath(__file__))

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
    out, para, lines, heads = [], [], md.strip().splitlines(), []
    def flush():
        if para: out.append("<p>" + "<br>".join(inline(l) for l in para) + "</p>"); para.clear()
    i = 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip(): flush(); i += 1; continue
        if l.startswith("# "): flush(); i += 1; continue  # the page title comes from the template
        m = re.match(r"## (\d+)\.\s*(.*)", l)
        if m: flush(); out.append(f'<h2 id="s{m.group(1)}">{m.group(1)}. {inline(m.group(2))}</h2>'); heads.append((f"s{m.group(1)}", f"{m.group(1)}. {inline(m.group(2))}")); i += 1; continue
        if l.startswith("## "): flush(); out.append(f"<h2>{inline(l[3:])}</h2>"); i += 1; continue
        if l.strip() == "---": flush(); out.append("<hr>"); i += 1; continue
        if l.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = ['<div class="table"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            t += ["<tr>" + "".join(f'<td data-label="{html.escape(head[j] if j < len(head) else "")}"><span>{inline(c)}</span></td>' for j, c in enumerate(r)) + "</tr>" for r in body]
            out.append("".join(t) + "</tbody></table></div>"); continue
        if l.startswith("- "):
            flush(); items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
        para.append(l.strip()); i += 1
    flush()
    return "\n".join(out), heads

CSS = """:root{color-scheme:light dark;--bg:#FFFFFF;--card:#FFFFFF;--text:#14284B;--muted:#4B5B78;--line:#E3E8F0;--tint:#FFF4EC;--wash:#F2F6FA;--link:#B84A08;--btn:#E8601C;--btn-text:#FFFFFF}
@media (prefers-color-scheme:dark){:root{--bg:#0F1623;--card:#172033;--text:#EEF2F8;--muted:#AAB7CC;--line:#2A3650;--tint:#2B2118;--wash:#131C2E;--link:#FF9F4A;--btn:#FF9F4A;--btn-text:#1F1205}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;accent-color:var(--btn);scrollbar-color:var(--muted) transparent}::selection{background:var(--btn);color:var(--btn-text)}
body:lang(ja){word-break:auto-phrase}body:lang(ko){word-break:keep-all;font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans CJK KR",sans-serif}.plan li{text-wrap:pretty}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang TC","PingFang SC","Hiragino Sans","Noto Sans CJK TC",sans-serif}
a{color:var(--link);text-underline-offset:.15em}
:focus-visible{outline:3px solid var(--link);outline-offset:2px;border-radius:4px}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}.prose{max-width:760px;padding-top:8px}
header{border-bottom:1px solid var(--line)}
.bar{display:flex;align-items:center;flex-wrap:wrap;gap:0 4px;min-height:68px;padding:4px 0}
.brand{display:flex;align-items:center;gap:10px;min-height:44px;font-weight:800;font-size:22px;text-decoration:none;color:var(--text);margin-right:auto;order:1}
.brand img{width:40px;height:40px;border-radius:10px}
.bar nav{display:flex;order:2}
.bar nav a,.lang summary{display:inline-flex;align-items:center;min-height:44px;padding:0 12px;color:var(--text);font-size:15px;font-weight:500;text-decoration:none}
.bar nav a[aria-current]{color:var(--link);font-weight:700}
.lang{position:relative;order:3}.lang summary{cursor:pointer;list-style:none;gap:6px}.lang summary::-webkit-details-marker{display:none}.lang summary::after{content:"▾";font-size:12px}
.lang .menu{position:absolute;right:0;top:100%;z-index:10;min-width:160px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:6px;box-shadow:0 8px 24px rgba(0,0,0,.16)}
.lang .menu a{display:flex;align-items:center;min-height:44px;padding:0 12px;border-radius:8px;color:var(--text);text-decoration:none}.lang .menu a[aria-current]{font-weight:700;color:var(--link)}
@media (max-width:560px){.bar nav{order:4;flex:1 0 100%;margin-left:-12px}.lang{order:2}}
main{padding:0 0 56px}
h1{font-size:34px;line-height:1.3;margin:28px 0 8px;text-wrap:balance}.prose h2{font-size:21px;margin:36px 0 10px;scroll-margin-top:16px;text-wrap:balance}
.meta{color:var(--muted);font-size:15px}
.hero{display:grid;gap:24px;align-items:center;padding:24px 0 0}
.hero h1{font-size:clamp(40px,7vw,68px);line-height:1.16;font-weight:800;margin:0 0 20px;letter-spacing:-.01em}
.hero-meta{font-size:clamp(20px,2.4vw,26px);line-height:1.4;font-weight:700;margin:0 0 12px}.hero-meta .rate{display:inline-block;white-space:nowrap;margin:4px 0 0 .5em;padding:0 14px;border-radius:999px;background:var(--wash);font-size:.78em}.hero-meta .rate::before{content:"";display:inline-block;width:.55em;height:.55em;margin-right:.5em;border-radius:50%;background:#F26A21;vertical-align:.04em;animation:beat 1.4s cubic-bezier(.16,1,.3,1) 4}
@keyframes beat{from{transform:scale(1.7);opacity:1}to{transform:scale(1);opacity:.8}}@media (prefers-reduced-motion:reduce){.hero-meta .rate::before{animation:none}}
.lead{font-size:19px;color:var(--muted);margin:0 0 14px;max-width:34em;text-wrap:balance;word-break:auto-phrase}
.soon{font-size:15px;color:var(--muted);margin:0 0 24px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:0 28px;border-radius:12px;background:var(--btn);color:var(--btn-text);font-size:19px;font-weight:700;text-decoration:none}
.hero-art{display:block;width:100%;height:auto}
:lang(ja) .hero h1{font-size:clamp(30px,5.2vw,48px);line-height:1.3;word-break:auto-phrase}
@media (min-width:900px){.hero{grid-template-columns:1fr 1.15fr;gap:32px;padding:40px 0 0}}
.features{display:grid;grid-template-columns:repeat(2,1fr);gap:32px 20px;margin-top:48px}.feature-art{display:block;width:min(100%,180px);height:auto;margin:0 0 8px -8px}.feature h2{font-size:22px}
@media (min-width:900px){.features{grid-template-columns:repeat(4,1fr);gap:32px}.feature h2{font-size:24px}}
.feature h2,.shots h2,.plans-sec h2{font-size:26px;line-height:1.3;margin:0 0 8px;text-wrap:balance}.feature p{margin:0;color:var(--muted)}
.band{background:var(--wash);margin-top:56px;padding:48px 0 40px}.plans-sec{padding-top:48px}
.shot-row{display:flex;gap:28px;overflow-x:auto;scroll-snap-type:x mandatory;padding:24px 8px 8px;margin:0 -8px}
.shot{position:relative;flex:0 0 min(58vw,250px);margin:0;scroll-snap-align:center;text-align:center}
.shot::before{content:"";position:absolute;z-index:0;left:-4%;right:-4%;top:14%;height:86%;border-radius:48px;background:linear-gradient(160deg,#FFB98A 0%,#F5A9BE 45%,#8FBDE6 100%);filter:blur(34px);opacity:.9}
.shot img{position:relative;z-index:1;display:block;width:100%;height:auto;border-radius:12.5%/5.75%;box-shadow:0 1px 2px rgba(20,40,75,.12)}
.shot figcaption{position:relative;z-index:1;margin-top:16px;font-size:15px;font-weight:600;color:var(--text);text-wrap:balance}
@media (prefers-color-scheme:dark){.shot::before{opacity:.35}}
@media (min-width:900px){.shot-row{overflow:visible;justify-content:center;gap:36px}.shot{flex:0 1 240px}}
.plans-lead{color:var(--muted);margin:0 0 16px}
.plans{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.plan{border:1px solid var(--line);border-radius:16px;padding:20px 22px;background:var(--card)}.plan.pro{border-color:var(--btn);border-width:2px;background:var(--tint)}
.plan h3{margin:0 0 8px;font-size:20px}.plan ul{margin:0;padding-left:1.2em}.plan li{margin:6px 0}
.faq details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:0 16px;margin:10px 0;scroll-margin-top:16px}.faq summary{cursor:pointer;font-weight:600;min-height:44px;padding:10px 0}.faq details p{margin:0 0 12px}.faq details:target{outline:2px solid var(--link)}
.contact{background:var(--tint);border-radius:14px;padding:16px 18px}
.toc{background:var(--tint);border-radius:14px;padding:14px 18px;margin:18px 0}.toc-title{font-weight:700;margin:0 0 4px}.toc ul{list-style:none;margin:0;padding:0;columns:2 280px}.toc a{display:block;padding:6px 0;text-decoration:none}
.table{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border:1px solid var(--line);padding:8px 10px;vertical-align:top;text-align:left}th{background:var(--tint)}
@media (max-width:640px){.table{overflow:visible}table,tbody,tr,td{display:block}thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
tr{border:1px solid var(--line);border-radius:12px;margin:0 0 12px;padding:4px 14px;background:var(--card)}td{border:0;padding:6px 0;display:grid;grid-template-columns:6.5em 1fr;gap:10px}td::before{content:attr(data-label);font-weight:600;color:var(--muted)}}
footer{color:var(--muted);font-size:14px;padding:0 0 40px}.footer-art{display:block;width:100%;max-width:960px;height:auto;margin:48px auto 0}footer .wrap{border-top:1px solid var(--line);padding-top:24px}footer p{margin:0 0 12px}footer ul{list-style:none;margin:0 0 8px;padding:0;display:flex;flex-wrap:wrap;gap:0 14px}footer li a{display:inline-flex;align-items:center;min-height:44px;color:var(--muted)}footer li a[aria-current]{font-weight:700}
"""

def page(lang, kind, title, body, depth, bare=False):
    t = T[lang]; up = "../" * depth
    def href(l, k): return f"{up}{l}/" + ("" if k == "home" else f"{k}/")
    nav = "".join(f'<a href="{href(lang, k)}"{" aria-current=page" if k == kind else ""}>{t["nav_" + k]}</a>' for k in ["support", "privacy"])
    langs = "".join(f'<a href="{href(l, kind)}" lang="{HTML_LANG[l]}" hreflang="{HTML_LANG[l]}"{" aria-current=true" if l == lang else ""}>{LANG_NAME[l]}</a>' for l in LANGS)
    flangs = "".join(f"<li>{a}</li>" for a in re.findall(r"<a [^>]+>[^<]+</a>", langs))
    alt = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{href(l, kind)}">' for l in LANGS)
    banner = f'<meta name="apple-itunes-app" content="app-id={APP_STORE_ID}">' if APP_STORE_ID else ""
    return f"""<!doctype html>
<html lang="{HTML_LANG[lang]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0F1623" media="(prefers-color-scheme: dark)">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(t['hero'])}">{banner}
<link rel="icon" href="{up}assets/icon-64.png"><link rel="apple-touch-icon" href="{up}assets/icon-180.png"><link rel="stylesheet" href="{up}assets/style.css">{alt}</head>
<body><header><div class="wrap"><div class="bar"><a class="brand" href="{href(lang, 'home')}"><img src="{up}assets/icon-64.png" alt="">{t['app']}</a><nav aria-label="{t['main_nav']}">{nav}</nav>
<details class="lang"><summary aria-label="{t['lang_label']}">{LANG_NAME[lang]}</summary><div class="menu">{langs}</div></details></div></div></header>
<main>{body if bare else '<div class="wrap">' + body + '</div>'}</main>
<footer><img class="footer-art" src="{up}assets/footer.webp" width="1800" height="600" alt="" loading="lazy"><div class="wrap"><p>{t['disclaimer']}</p><ul aria-label="{t['site_nav']}"><li><a href="{href(lang, 'support')}">{t['nav_support']}</a></li><li><a href="{href(lang, 'privacy')}">{t['nav_privacy']}</a></li><li><a href="{EULA}">{t['terms']}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul>
<ul aria-label="{t['lang_nav']}">{flangs}</ul><p>© 2026 Nex</p></div></footer>
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
if(/^zh-(hans|cn|sg|my)/.test(n))l='zh-Hans';else if(/^zh/.test(n))l='zh-Hant';else if(/^ja/.test(n))l='ja';else if(/^ko/.test(n))l='ko';
location.replace('{up}'+l+'/{suffix}'+location.hash);}})();</script></head>
<body><main><div class="wrap"><h1>跑拍 Jogbeat</h1><ul>{links}</ul></div></main></body></html>
"""

shutil.rmtree(OUT, ignore_errors=True); os.makedirs(f"{OUT}/assets")
write(f"{OUT}/assets/style.css", CSS)
for size in (64, 180, 256):
    subprocess.run(["sips", "-Z", str(size), f"{SRC}/icon-1024.png", "--out", f"{OUT}/assets/icon-{size}.png"], check=True, capture_output=True)
open(f"{OUT}/.nojekyll", "w").close()
for art in ("hero", "footer", *(f"feat-{k}" for k in FEATURE_ART)): shutil.copy(f"{HERE}/assets-src/{art}.webp", f"{OUT}/assets/{art}.webp")
for lang in LANGS:
    os.makedirs(f"{OUT}/assets/shots/{lang}")
    for n in SHOTS: shutil.copy(f"{HERE}/assets-src/shots/{lang}/{n}.webp", f"{OUT}/assets/shots/{lang}/{n}.webp")
write(f"{OUT}/index.html", redirect("home", 0))
write(f"{OUT}/privacy/index.html", redirect("privacy", 1))
write(f"{OUT}/support/index.html", redirect("support", 1))
write(f"{OUT}/404.html", '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>404 · 跑拍 Jogbeat</title><link rel="stylesheet" href="/JogBeat-Site/assets/style.css"></head><body><main><div class="wrap"><h1>404</h1><p><a href="/JogBeat-Site/">跑拍 Jogbeat</a></p></div></main></body></html>')

for lang in LANGS:
    t = T[lang]
    feats = "".join(f'<section class="feature"><img class="feature-art" src="../assets/feat-{k}.webp" width="600" height="600" alt="" loading="lazy"><h2>{h}</h2><p>{p}</p></section>' for k, (h, p) in zip(FEATURE_ART, t["features"]))
    shots = "".join(f'<figure class="shot"><img src="../assets/shots/{lang}/{n}.webp" width="520" height="1130" loading="lazy" alt="{html.escape(alt)}"><figcaption>{cap}</figcaption></figure>' for n, alt, cap in zip(SHOTS, t["shots_alt"], t["shots_caption"]))
    plan = lambda cls, ttl, items: f'<section class="plan {cls}"><h3>{ttl}</h3><ul>' + "".join(f"<li>{x}</li>" for x in items) + "</ul></section>"
    if APP_STORE_ID:
        # Launch day: Apple's official "Download on the App Store" badge (SVG kept in assets/, never hotlinked) goes here in place of this text link.
        store = f'<p class="soon"><a href="https://apps.apple.com/app/id{APP_STORE_ID}">{t["store_cta"]}</a></p>'
    else:
        store = f'<p class="soon">{t["soon"]}{"." if lang in ("en", "ko") else "。"}</p>'
    home = f"""<div class="wrap"><section class="hero"><div><h1>{t['hero_title']}</h1><p class="hero-meta">{t['tagline']}<span class="rate">{t['rate']}</span></p>
<p class="lead">{t['hero']}</p>{store}<a class="btn" href="support/#faq">{t['cta']}</a></div>
<img class="hero-art" src="../assets/hero.webp" width="1400" height="1050" alt="{html.escape(t['hero_alt'])}" fetchpriority="high"></section>
<div class="features">{feats}</div></div>
<section class="band"><div class="wrap"><h2>{t['shots_title']}</h2><div class="shot-row" role="group" tabindex="0" aria-label="{t['shots_label']}">{shots}</div></div></section>
<div class="wrap"><section class="plans-sec"><h2>{t['plans_title']}</h2><p class="plans-lead">{t['plans_lead']}</p><div class="plans">{plan('free', t['free_title'], t['free'])}{plan('pro', t['pro_title'], t['pro'])}</div></section></div>"""
    write(f"{OUT}/{lang}/index.html", page(lang, "home", f"{t['app']} — {t['tagline']}", home, 1, bare=True))

    faq = "".join(f'<details id="faq-{fid}"><summary>{q}</summary><p>{a}</p></details>' for fid, (q, a) in zip(FAQ_IDS, t["faq"]))
    support = f"""<div class="prose"><h1>{t['support_title']}</h1><p class="meta">{t['app']} · {t['tagline']}</p><p>{t['support_intro']}</p>
<section class="contact" id="contact"><h2 style="margin-top:0">{t['contact_title']}</h2><p>{t['contact_body'].format(e=EMAIL)}</p><p class="meta">{t['contact_tip']}</p></section>
<h2 id="faq">{t['faq_title']}</h2><div class="faq">{faq}</div>
<h2 id="terms">{t['terms']}</h2><p>{t['terms_note']} <a href="{EULA}">{EULA}</a></p></div>"""
    write(f"{OUT}/{lang}/support/index.html", page(lang, "support", f"{t['support_title']} — {t['app']}", support, 2))

    md = open(f"{SRC}/privacy.{lang}.md", encoding="utf-8").read()
    title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    body, heads = md_to_html(md)
    toc = f'<nav class="toc" aria-label="{t["toc_title"]}"><p class="toc-title">{t["toc_title"]}</p><ul>' + "".join(f'<li><a href="#{i}">{h}</a></li>' for i, h in heads) + "</ul></nav>"
    write(f"{OUT}/{lang}/privacy/index.html", page(lang, "privacy", title, f'<div class="prose"><h1>{inline(title)}</h1>\n{toc}\n{body}</div>', 2))
print("built", OUT)
