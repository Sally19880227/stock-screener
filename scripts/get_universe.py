"""
東証プライム市場の銘柄コード一覧を取得する。
JPXが公開している「東証上場銘柄一覧」Excelファイルを使用。
https://www.jpx.co.jp/markets/statistics-equities/misc/01.html
"""
import io
import os
import requests
import pandas as pd

JPX_LIST_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"


HEADERS = {
    # JPXサイトがブラウザ以外からのアクセスを弾くことがあるため、UAを偽装
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_prime_universe(cache_path: str = "data/universe.csv", max_retries: int = 3) -> pd.DataFrame:
    """東証プライム銘柄のコードと名称一覧を取得してDataFrameで返す。

    ネットワーク取得に失敗した場合は、
    1) 過去に保存したキャッシュ(cache_path)があればそれを使う
    2) キャッシュも無ければリポジトリ同梱のフォールバックリストを使う
    """
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(JPX_LIST_URL, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            df = pd.read_excel(io.BytesIO(resp.content))
            # JPXのファイルは列名が日本語（例: "コード", "銘柄名", "市場・商品区分"）
            df = df.rename(columns={
                "コード": "code",
                "銘柄名": "name",
                "市場・商品区分": "market",
                "33業種区分": "sector",
            })
            prime = df[df["market"].astype(str).str.contains("プライム", na=False)].copy()
            prime["code"] = prime["code"].astype(str).str.strip()
            prime = prime[["code", "name", "sector"]].dropna(subset=["code"])
            if len(prime) < 100:
                # プライム銘柄は1,600件前後のはず。極端に少なければ形式変更等を疑い失敗扱いにする
                raise ValueError(f"取得件数が異常に少ない: {len(prime)}件")
            prime.to_csv(cache_path, index=False)
            print(f"[info] JPXサイトから{len(prime)}件取得（{attempt}回目で成功）")
            return prime
        except Exception as e:
            last_error = e
            print(f"[warn] JPX一覧の取得に失敗（{attempt}/{max_retries}回目）: {e}")

    print(f"[warn] JPX一覧の取得が全て失敗しました: {last_error}")

    # 1) 前回実行時のキャッシュがあればそれを使う
    if os.path.exists(cache_path):
        print(f"[info] キャッシュ({cache_path})を使用します。")
        return pd.read_csv(cache_path, dtype={"code": str})

    # 2) キャッシュも無ければ同梱のフォールバックリストを使う
    fallback_path = os.path.join(os.path.dirname(__file__), "fallback_universe.csv")
    print(f"[info] 同梱フォールバックリスト({fallback_path})を使用します。")
    return pd.read_csv(fallback_path, dtype={"code": str})


if __name__ == "__main__":
    df = fetch_prime_universe()
    print(f"取得銘柄数: {len(df)}")
    print(df.head())
