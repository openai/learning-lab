from openai import OpenAI
from demo_util import color, function_to_schema
import json

# OpenAI クライアントの初期化
client = OpenAI()

# === デモループ ===

# 使用するモデルを定義
model = "gpt-4o-mini"

# アシスタントの動作を設定するためのシステムメッセージを定義
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

# 商品IDを検索する関数
def look_up_item(search_query):
    """商品IDを見つけるために使用します。
    検索クエリには説明やキーワードを使用できます。"""
    item_id = "item_132612938"
    print(color("見つかった商品:", "green"), item_id)
    return item_id

# 返金処理を実行する関数
def execute_refund(item_id, reason="not provided"):
    print(color("\n\n=== 返金概要 ===", "green"))
    print(color(f"商品ID: {item_id}", "green"))
    print(color(f"理由: {reason}", "green"))
    print("=================\n")
    print(color("返金の実行に成功しました！", "green"))
    return "success"

# 使用可能なツールを定義
tools = [execute_refund, look_up_item]

# アシスタントとの完全なやり取りを処理する関数
def run_full_turn(system_message, tools, messages):

    # ツールをスキーマに変換
    tool_schemas = [function_to_schema(f) for f in tools]

    # OpenAI API を呼び出してレスポンスを生成
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_message}] + messages,
        tools=tool_schemas,
    )
    message = response.choices[0].message
    messages.append(message)

    # アシスタントの応答を表示
    if message.content:
        print(color("Assistant:", "yellow"), message.content)

    # ツール呼び出しがない場合はメッセージを返す
    if not message.tool_calls:
        return message

    # ツール呼び出しがある場合、その詳細を表示
    for tool_call in message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        print(
            color("Assistant:", "yellow"),
            color(f"ツール呼び出しを実行中: {tool_call.function.name}({args})", "magenta"),
        )

    return message

# 会話メッセージの初期化
messages = []

# ユーザーと継続的に対話するループを開始
while True:
    # ユーザー入力を取得
    user = input(color("User: ", "blue") + "\033[90m")
    messages.append({"role": "user", "content": user})

    # 1回のやり取りを実行
    run_full_turn(system_message, tools, messages)
