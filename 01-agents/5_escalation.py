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
    # ダミーのアイテムIDを返す
    item_id = "item_132612938"
    print(color("見つかった商品:", "green"), item_id)
    return item_id

# 返金処理を実行する関数
def execute_refund(item_id, reason="not provided"):
    """指定された商品IDと理由を元に返金処理を実行します。"""
    print(color("\n\n=== 返金概要 ===", "green"))
    print(color(f"商品ID: {item_id}", "green"))
    print(color(f"理由: {reason}", "green"))
    print("=================\n")
    print(color("返金の実行に成功しました！", "green"))
    return "success"

# エスカレーションを人間の担当者に引き継ぐ関数
def escalate_to_human(summary):
    """明示的にリクエストされた場合のみ、この関数を呼び出します。"""
    print(color("人間の担当者にエスカレーション中...", "red"))
    print("\n=== エスカレーションレポート ===")
    print(f"概要: {summary}")
    print("========================\n")
    exit()

# 使用可能なツールを定義
tools = [execute_refund, look_up_item, escalate_to_human]

# アシスタントとの完全なやり取りを処理する関数
def run_full_turn(system_message, tools, messages):
    """アシスタントとの対話を処理し、必要に応じてツールを呼び出します。"""

    # 現在のメッセージ数を記録
    num_init_messages = len(messages)
    messages = messages.copy()

    while True:

        # Python 関数をツールに変換し、逆引きマップを保存
        tool_schemas = [function_to_schema(tool) for tool in tools]
        tools_map = {tool.__name__: tool for tool in tools}

        # === 1. OpenAI のコンプリートを取得 ===
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_message}] + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        # アシスタントの応答を表示
        if message.content:
            print(color("Assistant:", "yellow"), message.content)

        # ツール呼び出しがない場合はループを終了
        if not message.tool_calls:
            break

        # === 2. ツール呼び出しを処理 ===

        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tools_map)

            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            messages.append(result_message)

    # ==== 3. 新しいメッセージを返す =====
    return messages[num_init_messages:]

# ツール呼び出しを実行する関数
def execute_tool_call(tool_call, tools_map):
    """指定されたツール呼び出しを実行します。"""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(color("Assistant:", "yellow"), color(f"{name}({args})", "magenta"))

    # 指定された引数で対応する関数を呼び出す
    return tools_map[name](**args)

# 会話メッセージの初期化
messages = []

# ユーザーと継続的に対話するループを開始
while True:
    # ユーザー入力を取得
    user = input(color("User: ", "blue") + "\033[90m")
    messages.append({"role": "user", "content": user})

    # 新しいやり取りを実行
    new_messages = run_full_turn(system_message, tools, messages)
    messages.extend(new_messages)
