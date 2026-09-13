# 東証プライム 注目シグナル銘柄 自動スクリーニング

毎日、東証プライム全銘柄をテクニカル指標でスクリーニングし、
シグナルが出た銘柄と関連ニュースをHTMLレポート（GitHub Pages）として公開、
併せて自分宛にメール通知する仕組みです。

## できること・できないこと

- ✅ 複数のテクニカルシグナル（ゴールデンクロス、RSI反発、出来高急増、
  短期モメンタム、52週高値更新）を機械的にチェックし、根拠を提示
- ✅ 該当銘柄の関連ニュースを自動取得
- ❌ 株価上昇を保証・断定する予測は行いません（そもそも不可能です）
- ❌ 特定の有料/会員制「予測サイト」のスクレイピングは行っていません
  （利用規約違反や不安定さのリスクがあるため。無料の公開データのみ使用）

## セットアップ手順

### 1. GitHubリポジトリを作成

1. GitHubで新しいリポジトリを作成（例: `stock-screener`）。Public/Privateどちらでも可
   （Privateの場合もGitHub Pagesは利用可）。
2. このフォルダの中身を丸ごとそのリポジトリにpushする。

```bash
cd stock-screener
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/【あなたのユーザー名】/stock-screener.git
git push -u origin main
```

### 2. GitHub Pagesを有効化

1. リポジトリの `Settings` → `Pages`
2. "Build and deployment" の Source を `Deploy from a branch` に設定
3. Branch を `main`、フォルダを `/docs` に設定して Save
4. 数分後、`https://【ユーザー名】.github.io/stock-screener/` でページが公開される

### 3. Gmailのアプリパスワードを発行

1. Googleアカウントで2段階認証を有効化（まだの場合）
2. https://myaccount.google.com/apppasswords にアクセス
3. アプリ名を適当に入力（例: stock-screener）してパスワードを生成
4. 表示された16桁のパスワードをメモ（スペースは含めても除いてもOK）

**重要**: 通常のGmailログインパスワードではなく、このアプリパスワードを使います。

### 4. GitHub Secretsを設定

リポジトリの `Settings` → `Secrets and variables` → `Actions` → `New repository secret` で以下を追加：

| Secret名 | 内容 |
|---|---|
| `GMAIL_ADDRESS` | 送信元Gmailアドレス（例: yourname@gmail.com） |
| `GMAIL_APP_PASSWORD` | 手順3で発行したアプリパスワード |
| `MAIL_TO` | 送信先メールアドレス（自分宛でOK。GMAIL_ADDRESSと同じでも可） |
| `REPORT_URL` | 手順2で確認したGitHub PagesのURL |

### 5. 動作確認（手動実行）

1. リポジトリの `Actions` タブを開く
2. `Daily Stock Screening` ワークフローを選択
3. `Run workflow` ボタンで手動実行
4. 数十分後、メールが届き、GitHub Pagesのページが更新されることを確認

初回は東証プライム全銘柄（約1,600銘柄）のデータ取得のため、
30分〜1時間程度かかる可能性があります（GitHub Actions無料枠は月2,000分）。

### 6. 自動実行の確認

`.github/workflows/daily.yml` の cron設定により、
平日（月〜金, UTC基準で0-4 = 日本時間の月〜金朝）の日本時間6:30ごろに自動実行されます。
時間を変更したい場合は `daily.yml` 内の `cron` の値を編集してください
（GitHub Actionsのcronは分単位でズレることがあります）。

## 実行時間・無料枠について

- GitHub Actions 無料枠: パブリックリポジトリは無制限、プライベートリポジトリは月2,000分
- 全銘柄（約1,600件）のyfinance取得は1銘柄あたり待機込みで実行するため、
  実行に30分前後かかる想定です。プライベートリポジトリで毎日実行すると
  月900分程度消費する計算になるため、余裕はありますが、
  もし超過が心配であれば対象を日経225などに絞ることも可能です。

## ファイル構成

```
stock-screener/
├── .github/workflows/daily.yml   # 自動実行の定義
├── scripts/
│   ├── get_universe.py           # 東証プライム銘柄一覧取得
│   ├── screen.py                 # テクニカル指標計算・スクリーニング
│   ├── news.py                   # 関連ニュース取得
│   ├── build_report.py           # HTMLレポート生成
│   ├── send_mail.py              # メール送信
│   └── main.py                   # 全体の実行フロー
├── docs/                         # GitHub Pagesで公開されるフォルダ
├── data/                         # 銘柄一覧のキャッシュ
└── requirements.txt
```

## シグナルの意味（本レポートが提示する「根拠」）

| シグナル | 意味 |
|---|---|
| ゴールデンクロス | 5日移動平均線が25日移動平均線を上抜け。短期トレンド転換のサインとされる |
| RSI反発 | RSI（14日）が30を下回る「売られすぎ」水準から回復 |
| 出来高急増 | 直近出来高が20日平均の2倍以上。材料への市場反応の可能性 |
| 短期モメンタム上昇 | 直近5営業日で8%以上上昇 |
| 52週高値更新 | 直近1年の高値を更新 |

これらはあくまで過去データに基づく「よく参照される」パターンであり、
将来の値動きを保証するものではありません。
