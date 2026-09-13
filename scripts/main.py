"""
毎日実行するメインスクリプト。
1. 東証プライム銘柄一覧を取得
2. 全銘柄をスクリーニング（シグナル抽出）
3. 上位銘柄の関連ニュースを取得
4. HTMLレポートを生成（docs/index.html）
5. メールで通知
"""
import os
import sys

sys.path.append(os.path.dirname(__file__))

from get_universe import fetch_prime_universe
from screen import screen_universe
from news import fetch_news_for
from build_report import build_html, save_report
from send_mail import send_report_mail

TOP_N_FOR_NEWS = 30  # ニュース取得はAPI負荷軽減のため上位N件のみ


def main():
    print("[1/5] 銘柄一覧を取得中...")
    universe_df = fetch_prime_universe(cache_path="data/universe.csv")
    codes = universe_df["code"].astype(str).tolist()
    print(f"  対象銘柄数: {len(codes)}")

    print("[2/5] スクリーニング実行中（数十分かかる場合があります）...")
    results = screen_universe(codes)
    print(f"  シグナル該当銘柄数: {len(results)}")

    print("[3/5] 上位銘柄の関連ニュースを取得中...")
    name_map = dict(zip(universe_df["code"].astype(str), universe_df["name"]))
    news_map = {}
    for r in results[:TOP_N_FOR_NEWS]:
        company_name = name_map.get(r["code"], r["code"])
        news_map[r["code"]] = fetch_news_for(company_name)

    print("[4/5] HTMLレポート生成中...")
    html_str = build_html(results, universe_df, news_map, top_n=TOP_N_FOR_NEWS)
    os.makedirs("docs", exist_ok=True)
    save_report(html_str, path="docs/index.html")

    print("[5/5] メール送信中...")
    send_report_mail(results, universe_df)

    print("完了")


if __name__ == "__main__":
    main()
