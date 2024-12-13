from openai import OpenAI
from demo_util import color
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

# アシスタントが利用できるツールを定義
# これらのツールは、商品検索や返金処理などの外部操作を模擬します
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_refund",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["item_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "look_up_item",
            "description": "商品IDを見つけるために使用します。\n    検索クエリには説明やキーワードを使用できます。",
            "parameters": {
                "type": "object",
                "properties": {"search_query": {"type": "string"}},
                "required": ["search_query"],
            },
        },
    },
]

# アシスタントとの完全なやり取りを処理する関数
def run_full_turn(system_message, tools, messages):
    # OpenAI API を呼び出してレスポンスを生成
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_message}] + messages,
        tools=tools,
    )

    # レスポンスからアシスタントのメッセージを抽出
    message = response.choices[0].message
    messages.append(message)

    # ユーザーへのアシスタントの応答を表示
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
