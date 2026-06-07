import os
import re
import json
import random
import hashlib
import datetime
import feedparser
import anthropic

RSS_FEEDS = [
    "https://www.agerpres.ro/rss/cultura",
    "https://www.digi24.ro/rss/stiri/cultura",
    "https://www.g4media.ro/category/cultura/feed",
    "https://news.google.com/rss/search?q=arta+Romania+expozitie&hl=ro&gl=RO&ceid=RO:ro",
    "https://news.google.com/rss/search?q=artist+roman+premiu&hl=ro&gl=RO&ceid=RO:ro",
]

UNSPLASH_IMAGES = [
    "https://images.unsplash.com/photo-1561214115-f2f134cc4912?auto=format&fit=crop&w=500&h=280&q=80",
    "https://images.unsplash.com/photo-1578926288207-a90a5366759d?auto=format&fit=crop&w=500&h=280&q=80",
    "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=500&h=280&q=80",
    "https://images.unsplash.com/photo-1541961017774-22349e4a1262?auto=format&fit=crop&w=500&h=280&q=80",
    "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=500&h=280&q=80",
    "https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?auto=format&fit=crop&w=500&h=280&q=80",
]


def fetch_news_items(max_items=10):
    seen_hashes = set()
    items = []
    keywords = ["arta", "artist", "expozit", "muzeu", "cultura",
                "pictura", "sculptura", "teatru", "film", "muzica",
                "brancusi", "galerie", "festiv", "premiu", "concert"]

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                title = entry.get("title", "").strip()
                if not title or len(title) < 15:
                    continue
                title_hash = hashlib.md5(title.lower().encode()).hexdigest()
                if title_hash in seen_hashes:
                    continue
                seen_hashes.add(title_hash)
                text_lower = (title + entry.get("summary", "")).lower()
                if not any(kw in text_lower for kw in keywords):
                    continue
                items.append({
                    "title": title,
                    "summary": entry.get("summary", "")[:500],
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", feed_url),
                })
                if len(items) >= max_items:
                    return items
        except Exception as e:
            print(f"[WARN] Feed {feed_url} esuat: {e}")
    return items


def generate_article_with_claude(news_items):
    if not news_items:
        return None

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    news_context = "\n\n".join([
        f"STIRE {i+1}:\nTitlu: {item['title']}\nSursa: {item['source']}\nRezumat: {item['summary']}\nLink: {item['link']}"
        for i, item in enumerate(news_items[:5])
    ])

    prompt = f"""Esti redactorul cultural al asociatiei Alter Spero din Bucuresti.

Stiri recente despre arta si cultura din Romania:

{news_context}

Scrie un articol de blog pentru sectiunea Jurnal cultural de pe alterspero.ro.
Alege cel mai interesant subiect. Scrie in romana, ton cald, ~400 cuvinte.

Raspunde EXCLUSIV in format JSON valid, fara markdown, fara text inainte sau dupa:

{{
  "titlu": "titlul articolului (max 80 caractere)",
  "categorie": "Articole",
  "rezumat": "2 fraze introductive (max 200 caractere)",
  "continut": "textul complet cu paragrafe HTML simple folosind doar taguri p si strong",
  "durata_citire": 4,
  "link_sursa": "URL-ul stirii sursa",
  "slug": "titlu-cu-cratime-fara-diacritice"
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        print(f"[ERROR] Claude API: {e}")
        return None


def build_article_html(article, image_url):
    now = datetime.datetime.now()
    months_ro = {
        1: "Ianuarie", 2: "Februarie", 3: "Martie", 4: "Aprilie",
        5: "Mai", 6: "Iunie", 7: "Iulie", 8: "August",
        9: "Septembrie", 10: "Octombrie", 11: "Noiembrie", 12: "Decembrie"
    }
    date_str = f"{months_ro[now.month]} {now.year}"
    durata = article.get("durata_citire", 4)
    categorie = article.get("categorie", "Articole")
    titlu = article.get("titlu", "")
    rezumat = article.get("rezumat", "")
    continut = article.get("continut", "")
    link_sursa = article.get("link_sursa", "#")

    sursa_html = ""
    if link_sursa and link_sursa != "#":
        sursa_html = f'<p><em>Sursa: <a href="{link_sursa}" target="_blank" rel="noopener">articol original</a></em></p>'

    return f"""
                <div class="journal-card">
                    <img src="{image_url}" alt="{titlu}" style="width:100%;height:200px;object-fit:cover;border-radius:8px 8px 0 0;">
                    <div style="padding:1.25rem 1.5rem 1.5rem;">
                        <div style="font-size:.78rem;color:#888;margin-bottom:.6rem;">{categorie} &nbsp;·&nbsp; {date_str} &nbsp;·&nbsp; {durata} min citire</div>
                        <h3 style="font-size:1.1rem;font-weight:700;margin:0 0 .75rem;line-height:1.4;">{titlu}</h3>
                        <p style="font-size:.9rem;color:#555;line-height:1.6;margin:0 0 1rem;">{rezumat}</p>
                        <details>
                            <summary style="cursor:pointer;font-size:.85rem;font-weight:600;padding:.5rem 0;border-top:1px solid rgba(0,0,0,.08);">Citeste integral</summary>
                            <div style="padding-top:1rem;font-size:.9rem;line-height:1.75;color:#333;">
                                {continut}
                                {sursa_html}
                            </div>
                        </details>
                    </div>
                </div>"""


def inject_article_into_html(index_path, new_article_html):
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Nu gasesc {index_path}")
        return False

    marker_start = "<!-- JURNAL-ARTICLES-START -->"
    marker_end = "<!-- JURNAL-ARTICLES-END -->"

    if marker_start not in content or marker_end not in content:
        print("[ERROR] Markerii JURNAL nu exista in index.html.")
        return False

    before = content.split(marker_start)[0]
    existing_block = content.split(marker_start)[1].split(marker_end)[0]
    after = content.split(marker_end)[1]

    existing_count = existing_block.count('<div class="journal-card">')
    if existing_count >= 5:
        last_idx = existing_block.rfind('<div class="journal-card">')
        existing_block = existing_block[:last_idx]

    new_content = (
        before + marker_start
        + "\n" + new_article_html
        + existing_block
        + marker_end + after
    )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[OK] Articol injectat in {index_path}")
    return True


def save_article_log(article, log_path="scripts/articles_log.json"):
    from pathlib import Path
    log_file = Path(log_path)
    log = []
    if log_file.exists():
        try:
            log = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            log = []
    log.append({
        "slug": article.get("slug"),
        "titlu": article.get("titlu"),
        "data": datetime.datetime.now().isoformat(),
    })
    log = log[-50:]
    log_file.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    print("=" * 50)
    print(f"AlterSpero Content Bot — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    index_path = os.environ.get("SITE_INDEX_PATH", "index.html")

    print("\n[1/4] Colectare stiri RSS...")
    news_items = fetch_news_items(max_items=10)
    print(f"      -> {len(news_items)} stiri gasite")

    if not news_items:
        print("[ABORT] Nicio stire relevanta.")
        return

    print("\n[2/4] Generare articol cu Claude...")
    article = generate_article_with_claude(news_items)
    if not article:
        print("[ABORT] Generarea a esuat.")
        return
    print(f"      -> \"{article.get('titlu', 'N/A')}\"")

    print("\n[3/4] Construire HTML...")
    image_url = random.choice(UNSPLASH_IMAGES)
    article_html = build_article_html(article, image_url)

    print("\n[4/4] Injectare in site...")
    success = inject_article_into_html(index_path, article_html)
    if not success:
        return

    save_article_log(article)
    print(f"\n✓ Publicat: {article.get('titlu')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
