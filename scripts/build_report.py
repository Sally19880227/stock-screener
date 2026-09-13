"""
スクリーニング結果をHTMLレポートに整形する。
出力先: docs/index.html （GitHub Pagesの公開対象フォルダ）
"""
import datetime
import html


DISCLAIMER = (
    "本レポートは公開されている株価データとニュースから機械的に算出した"
    "テクニカル指標・材料の一覧であり、将来の株価上昇を保証・予測するものではありません。"
    "投資判断は自己責任で行ってください。"
)


def build_html(results: list[dict], universe_df, news_map: dict, top_n: int = 30) -> str:
    today = datetime.date.today().strftime("%Y年%m月%d日")
    name_map = dict(zip(universe_df["code"].astype(str), universe_df["name"]))

    rows_html = []
    for r in results[:top_n]:
        code = r["code"]
        name = name_map.get(code, code)
        signals_html = "".join(
            f"<li><strong>{html.escape(s['name'])}</strong>: {html.escape(s['detail'])}</li>"
            for s in r["signals"]
        )
        news_items = news_map.get(code, [])
        news_html = "".join(
            f'<li><a href="{html.escape(n["link"])}" target="_blank" rel="noopener">'
            f'{html.escape(n["title"])}</a></li>'
            for n in news_items
        ) or "<li>関連ニュースなし</li>"

        rows_html.append(f"""
        <div class="card">
          <h2>{html.escape(str(name))}（{html.escape(code)}）
            <span class="score">シグナル数: {r['score']}</span>
          </h2>
          <p class="price">終値: {r['last_close']} 円</p>
          <h3>該当した根拠</h3>
          <ul class="signals">{signals_html}</ul>
          <h3>関連ニュース</h3>
          <ul class="news">{news_html}</ul>
        </div>
        """)

    body = "\n".join(rows_html) if rows_html else "<p>本日は該当銘柄がありませんでした。</p>"

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>東証プライム 注目シグナル銘柄 - {today}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", sans-serif;
          max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f7; color: #1d1d1f; }}
  h1 {{ font-size: 1.4em; }}
  .disclaimer {{ background: #fff3cd; border: 1px solid #ffe69c; padding: 12px; border-radius: 8px;
                 font-size: 0.85em; margin-bottom: 20px; }}
  .card {{ background: #fff; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px;
           box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .card h2 {{ margin: 0 0 6px 0; font-size: 1.15em; display: flex; justify-content: space-between; }}
  .score {{ font-size: 0.7em; background: #eee; padding: 2px 8px; border-radius: 12px; color: #555; }}
  .price {{ color: #555; margin: 0 0 10px 0; }}
  h3 {{ font-size: 0.9em; margin: 12px 0 4px 0; color: #444; }}
  ul {{ margin: 4px 0; padding-left: 20px; font-size: 0.9em; }}
  .news a {{ color: #0066cc; text-decoration: none; }}
  .news a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
  <h1>東証プライム 注目シグナル銘柄一覧（{today}）</h1>
  <div class="disclaimer">{DISCLAIMER}</div>
  {body}
</body>
</html>"""


def save_report(html_str: str, path: str = "docs/index.html"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_str)
