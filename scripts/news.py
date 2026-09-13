"""
Googleニュースの無料RSSフィードを使い、銘柄名に関連する直近ニュースを取得する。
（Googleニュースの公開RSSエンドポイントは無料・無認証で利用可能）
"""
import urllib.parse
import feedparser  # requirements.txt に追加済み


def fetch_news_for(company_name: str, max_items: int = 3) -> list[dict]:
    """銘柄名で日本語ニュースを検索し、タイトルとリンクのリストを返す。"""
    query = urllib.parse.quote(f"{company_name} 株")
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"[warn] ニュース取得失敗 ({company_name}): {e}")
        return []

    items = []
    for entry in feed.entries[:max_items]:
        items.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return items
