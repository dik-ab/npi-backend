# NPI Backend

## 概要
メール送信のみのAPI

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
```

必要に応じて、環境変数 SENDER_EMAIL に送信元アドレスを設定ください。

###　単体テスト

```bash
docker-compose exec django /bin/bash
```

```bash
python manage.py test
```

###　リクエスト方法

```bash
curl -X POST http://127.0.0.1:8000/send-mail/ \
     -H "Content-Type: application/json" \
     -d '{
           "recipient_email": "example@domain.com",
           "subject": "Hello!",
           "message": "This is a test message sent from our API."
         }'
```
