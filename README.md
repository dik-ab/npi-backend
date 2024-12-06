# NPI Backend

## 概要
ユーザーアプリ・運用アプリのAPI

## 目次
- [インストール](#インストール)
- [使用方法](#使用方法)

## インストール
以下の手順に従ってプロジェクトをインストールしてください。

```bash
git clone https://github.com/yourusername/npi-backend.git
```

## 使用方法
プロジェクトを起動するには、以下のコマンドを実行してください。

```bash
docker-compose up -d
source venv/bin/activate ※仮想環境を起動する場合
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations ※migrationsファイルの作成 ・モデルに変更をした場合のみ。
python manage.py migrate
python manage.py runserver
deactivate ※仮想環境を終了する場合
docker-compose --rmi all
```

必要に応じて、環境変数 SENDER_EMAIL に送信元アドレスを設定ください。

## ディレクトリ構成
- `npi/` - Djangoプロジェクトのディレクトリ
- `shared/` - 共通参照モデルの管理用ディレクトリ
- `user-app/` - ユーザーアプリのディレクトリ
- `operation-app/` - 運用アプリのディレクトリ

##　単体テスト

```bash
python manage.py test
```

## ローカル検証用準備
- /etc/hostsに以下を追加 ※既存の設定はそのままでOK
```bash
127.0.0.1       user-app.localhost
127.0.0.1       operation-app.localhostst
```

###　リクエスト方法
- ローカルの場合
  http://user-app.localhost:8000/~~
  http://operation-app:8000/

- ECSの場合
  http://user-app.ドメイン/~~
  http://operation-app.ドメイン/~~

```bash
curl -X POST http://user-app.localhost:8000/send-mail/ \
     -H "Content-Type: application/json" \
     -d '{
           "recipient_email": "example@domain.com",
           "subject": "Hello!",
           "message": "This is a test message sent from our API."
         }'
```
