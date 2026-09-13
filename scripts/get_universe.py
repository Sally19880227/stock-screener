"""
東証プライム市場の銘柄コード一覧を取得する。
JPXが公開している「東証上場銘柄一覧」Excelファイルを使用。
https://www.jpx.co.jp/markets/statistics-equities/misc/01.html
"""
import io
import requests
import pandas as pd

JPX_LIST_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"


def fetch_prime_universe(cache_path: str = "data/universe.csv") -> pd.DataFrame:
    """東証プライム銘柄のコードと名称一覧を取得してDataFrameで返す。

    ネットワーク取得に失敗した場合はキャッシュ(cache_path)があればそれを使う。
    """
    try:
        resp = requests.get(JPX_LIST_URL, timeout=30)
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
        prime.to_csv(cache_path, index=False)
        return prime
    except Exception as e:
        print(f"[warn] JPX一覧の取得に失敗: {e}. キャッシュを使用します。")
        return pd.read_csv(cache_path)


if __name__ == "__main__":
    df = fetch_prime_universe()
    print(f"取得銘柄数: {len(df)}")
    print(df.head())
