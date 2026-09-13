"""
株価データを取得し、テクニカル指標ベースの「注目シグナル」を計算する。

方針:
  ・「上がる」ことを断定的に予測するのではなく、
    過去に注目されやすいとされるテクニカルパターンを
    複数チェックし、該当した項目を根拠として提示する。
  ・シグナル数が多い銘柄を上位表示するが、
    あくまで「材料が重なっている」という透明な表示に留める。
"""
import time
import pandas as pd
import yfinance as yf

# yfinanceでは東証銘柄は "コード.T" 形式
def to_yf_ticker(code: str) -> str:
    return f"{code}.T"


def compute_signals(hist: pd.DataFrame) -> list[dict]:
    """1銘柄分の日足データ(hist)からシグナルのリストを返す。

    hist: yfinanceのhistory()で取得したDataFrame（Close, Volumeなどを含む）
    """
    signals = []
    if hist is None or len(hist) < 30:
        return signals

    close = hist["Close"]
    volume = hist["Volume"]

    # --- 1. ゴールデンクロス（5日線が25日線を上抜け） ---
    ma5 = close.rolling(5).mean()
    ma25 = close.rolling(25).mean()
    if len(ma5) >= 2 and len(ma25) >= 2:
        if ma5.iloc[-2] <= ma25.iloc[-2] and ma5.iloc[-1] > ma25.iloc[-1]:
            signals.append({
                "name": "ゴールデンクロス",
                "detail": "直近で5日移動平均線が25日移動平均線を上抜けました。短期的な上昇トレンド転換のサインとされます。"
            })

    # --- 2. RSIが売られすぎ水準から反発 ---
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    if len(rsi) >= 2:
        if rsi.iloc[-2] < 30 and rsi.iloc[-1] >= 30:
            signals.append({
                "name": "RSI反発（売られすぎ圏からの回復）",
                "detail": f"RSIが30を下回る「売られすぎ」水準から回復しました（直近値: {rsi.iloc[-1]:.1f}）。自律反発が期待される局面です。"
            })

    # --- 3. 出来高急増（直近が20日平均の2倍以上） ---
    vol_avg20 = volume.rolling(20).mean()
    if len(vol_avg20) >= 1 and vol_avg20.iloc[-1] > 0:
        ratio = volume.iloc[-1] / vol_avg20.iloc[-1]
        if ratio >= 2.0:
            signals.append({
                "name": "出来高急増",
                "detail": f"直近の出来高が20日平均の{ratio:.1f}倍に増加しました。何らかの材料に市場が反応している可能性があります。"
            })

    # --- 4. 直近5日で大幅上昇（モメンタム） ---
    if len(close) >= 6:
        pct_5d = (close.iloc[-1] / close.iloc[-6] - 1) * 100
        if pct_5d >= 8:
            signals.append({
                "name": "短期モメンタム上昇",
                "detail": f"直近5営業日で株価が{pct_5d:.1f}%上昇しています。上昇トレンドが継続するか注目されます。"
            })

    # --- 5. 52週高値更新 ---
    if len(close) >= 252:
        high_252 = close.iloc[-252:].max()
        if close.iloc[-1] >= high_252 * 0.999:
            signals.append({
                "name": "52週高値更新",
                "detail": "株価が52週（約1年）ぶりの高値水準を更新しています。"
            })

    return signals


def screen_universe(codes: list[str], sleep_sec: float = 0.3) -> list[dict]:
    """銘柄コードのリストを受け取り、シグナルが1つ以上ある銘柄の結果を返す。"""
    results = []
    for code in codes:
        ticker = to_yf_ticker(code)
        try:
            hist = yf.Ticker(ticker).history(period="1y", interval="1d")
        except Exception as e:
            print(f"[warn] {ticker} 取得失敗: {e}")
            continue

        signals = compute_signals(hist)
        if signals:
            last_close = hist["Close"].iloc[-1] if len(hist) else None
            results.append({
                "code": code,
                "yf_ticker": ticker,
                "last_close": round(float(last_close), 1) if last_close else None,
                "signals": signals,
                "score": len(signals),
            })
        time.sleep(sleep_sec)  # レート制限対策

    results.sort(key=lambda r: r["score"], reverse=True)
    return results


if __name__ == "__main__":
    # 動作確認用のサンプル
    sample_codes = ["7203", "6758", "9984"]
    res = screen_universe(sample_codes)
    for r in res:
        print(r["code"], r["score"], [s["name"] for s in r["signals"]])
