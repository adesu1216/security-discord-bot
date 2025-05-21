# Security Discord Bot

## 🔐 概要
このBotは、Discordサーバーのセキュリティを強化するために作成されました。  
荒らし対策・警告・BAN・ログ表示など、管理を自動化する機能が揃っています。

## 📦 使用技術
- Python 3.11
- discord.py
- dotenv（環境変数でトークン管理）

## 🚀 機能一覧
- `/warn @ユーザー`：警告を与え、回数に応じて処罰（例：timeoutやBAN）
- `/ban @ユーザー`：管理者が直接BAN
- `/panic`：サーバー全体の書き込みを一時ロック
- `/log`：警告や処罰の履歴を表示
- `/reset_warnings`：警告数をリセット
- `/set_ad_channel`：宣伝チャンネルの登録
- `/remove_ad_channel`：登録解除
- `/view_ad_channels`：現在の許可リスト表示

## ⚙️ セットアップ方法
```bash
git clone https://github.com/adesu1216/security-discord-bot.git
cd security-discord-bot
pip install -r requirements.txt
python main.py
