"""Atualiza as seções automáticas do README. Só stdlib; roda local e no GitHub Actions.

- Vídeos: feed RSS do canal @gamedevjuan -> cards SVG do ytcards.demolab.com
- Artigos: RSS do blog (cursogame.dev/rss.xml). O feed ainda sai com o domínio do template
  (nurriyad.com) nos links e datas trocadas, então os links são reescritos e a data não aparece.
"""
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

README = "README.md"
CHANNEL_ID = "UCWsT-eyEeUU_HYA3qbt5UwA"
MAX_VIDEOS = 6
BLOG_FEED = "https://cursogame.dev/rss.xml"
MAX_POSTS = 10
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "JuanxCursed-profile"})
    return ET.fromstring(urllib.request.urlopen(req, timeout=30).read())


def video_cards():
    root = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}")
    cards = []
    for entry in root.findall("a:entry", NS)[:MAX_VIDEOS]:
        vid = entry.findtext("yt:videoId", namespaces=NS)
        title = re.sub(r"\s*#shorts\b", "", entry.findtext("a:title", namespaces=NS), flags=re.I).strip()
        ts = int(datetime.fromisoformat(entry.findtext("a:published", namespaces=NS)).timestamp())
        params = urllib.parse.urlencode({
            "id": vid, "title": title, "lang": "pt", "timestamp": ts,
            "background_color": "#111822", "title_color": "#EDF1F5", "stats_color": "#8b949e",
            "width": 250, "border_radius": 6, "max_title_lines": 2,
        })
        alt = title.replace('"', "&quot;")
        cards.append(
            f'<a href="https://www.youtube.com/watch?v={vid}"><img src="https://ytcards.demolab.com/?{params}" '
            f'alt="{alt}" title="{alt}" width="250" /></a>'
        )
    # grade 3 colunas alinhada no topo: card com título de 1 linha é mais baixo e desalinha num <p>
    rows = ["<tr>" + "".join(f'<td valign="top">{c}</td>' for c in cards[i:i + 3]) + "</tr>" for i in range(0, len(cards), 3)]
    return '<table align="center">\n' + "\n".join(rows) + "\n</table>"


def blog_posts():
    lines = []
    for item in fetch(BLOG_FEED).iter("item"):
        title = (item.findtext("title") or "").strip()
        link = re.sub(r"^https?://[^/]+", "https://cursogame.dev", (item.findtext("link") or "").strip())
        if title and link:
            lines.append(f"- [{title}]({link})")
        if len(lines) == MAX_POSTS:
            break
    return "\n".join(lines)


def replace_block(text, name, content):
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    block = f"{start}\n{content}\n{end}"
    return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S)


readme = open(README, encoding="utf-8").read()
readme = replace_block(readme, "YOUTUBE", video_cards())
readme = replace_block(readme, "BLOG", blog_posts())
open(README, "w", encoding="utf-8", newline="\n").write(readme)
print("README atualizado")
