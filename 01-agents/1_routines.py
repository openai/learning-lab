from openai import OpenAI
from demo_util import color

# OpenAI クライアントの初期化
client = OpenAI()

# === デモループ ===

# 使用するモデルを定義
model = "gpt-4o-mini"

# アシスタントの振る舞いを設定するためのシステムメッセージ
system_message = (
    "あなたはACME Inc.のカスタマーサポート担当者です。"
    "常に1文以内で回答してください。"
    "以下の手順に従ってユーザーと対話してください:"
    "1. 最初に質問をして、ユーザーの問題を深く理解してください。\n"
    " - ただし、ユーザーが既に理由を提供している場合を除きます。\n"
    "2. 修正案を提案してください（適当なものを考え出してください）。\n"
    "3. ユーザーが満足しない場合のみ、返金を提案してください。\n"
    "4. ユーザーが受け入れた場合、IDを検索して返金を実行してください。"
    ""
)

# メッセージ履歴を保存するリストを初期化
messages = []

# ユーザーとの対話を開始するループ
while True:
    # ユーザーの入力を取得
    user = input(color("User: ", "blue") + "\033[90m")
    messages.append({"role": "user", "content": user})  # ユーザーのメッセージを履歴に追加

    # モデルからの応答を取得
    response = client.chat.completions.create(
        model=model,  # 使用するモデルを指定
        messages=[{"role": "system", "content": system_message}] + messages,  # システムメッセージと履歴を送信
    )

    # モデルからの応答メッセージを抽出
    message = response.choices[0].message

    # アシスタントの応答を出力
    print(color("Assistant:", "yellow"), message.content)

    # モデルの応答を履歴に追加
    messages.append(message)