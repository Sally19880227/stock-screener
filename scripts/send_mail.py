"""
Gmail(SMTP)経由で、生成したレポートページへのリンクをメール送信する。

必要な環境変数（GitHub Secretsに設定）:
  GMAIL_ADDRESS      : 送信元Gmailアドレス
  GMAIL_APP_PASSWORD : Googleの「アプリパスワード」（通常のパスワードではない）
  MAIL_TO            : 送信先メールアドレス（自分宛でOK）
  REPORT_URL         : GitHub PagesのURL（例: https://yourname.github.io/stock-screener/）
"""
import os
import smtplib
import datetime
from email.mime.text import MIMEText


def send_report_mail(top_results: list[dict], universe_df) -> None:
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    mail_to = os.environ["MAIL_TO"]
    report_url = os.environ["REPORT_URL"]

    today = datetime.date.today().strftime("%Y年%m月%d日")
    name_map = dict(zip(universe_df["code"].astype(str), universe_df["name"]))

    lines = [f"{today} 東証プライム 注目シグナル銘柄（上位{min(10, len(top_results))}件）", ""]
    for r in top_results[:10]:
        name = name_map.get(r["code"], r["code"])
        signal_names = "、".join(s["name"] for s in r["signals"])
        lines.append(f"・{name}（{r['code']}） シグナル{r['score']}件: {signal_names}")

    lines.append("")
    lines.append(f"詳細（根拠・関連ニュース付き）はこちら: {report_url}")
    lines.append("")
    lines.append("※本メールは投資助言ではありません。投資判断は自己責任でお願いします。")

    body = "\n".join(lines)

    msg = MIMEText(body)
    msg["Subject"] = f"【株スクリーニング】{today} 注目シグナル銘柄"
    msg["From"] = gmail_address
    msg["To"] = mail_to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.send_message(msg)

    print("メール送信完了")
