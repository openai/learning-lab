from openai import OpenAI
from demo_util import color, function_to_schema
import json
from pydantic import BaseModel

# === クラス定義 ===

class Agent(BaseModel):
    """エージェントを表現するクラス"""
    name: str = "Agent"
    model: str = "gpt-4o"
    instructions: str = "You are a helpful Agent"
    tools: list = []

class Response(BaseModel):
    """応答を表現するクラス"""
    messages: list

# OpenAI クライアントの初期化
client = OpenAI()

# === デモループ ===

def run_full_turn(agent, messages):
    """1回のやり取りを処理する関数"""

    # 初期メッセージ数を記録
    num_init_messages = len(messages)
    messages = messages.copy()

    while True:

        # ツールをスキーマに変換してマッピングを保存
        tool_schemas = [function_to_schema(tool) for tool in agent.tools]
        tools_map = {tool.__name__: tool for tool in agent.tools}

        # === 1. OpenAI の応答を取得 ===
        response = client.chat.completions.create(
            model=agent.model,
            messages=[{"role": "system", "content": agent.instructions}] + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        if message.content:  # アシスタントの応答を表示
            print(color("Assistant:", "yellow"), message.content)

        if not message.tool_calls:  # ツール呼び出しがない場合は終了
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


def execute_tool_call(tool_call, tools_map):
    """指定されたツールを実行する関数"""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(color("Assistant:", "yellow"), color(f"{name}({args})", "magenta"))

    # 対応する関数を引数付きで呼び出す
    return tools_map[name](**args)

# === ツール定義 ===

def look_up_item(search_query):
    """商品IDを検索する関数"""
    item_id = "item_132612938"
    print(color("見つかった商品:", "green"), item_id)
    return item_id


def execute_refund(item_id, reason="not provided"):
    """返金処理を実行する関数"""
    print(color("\n\n=== 返金概要 ===", "green"))
    print(color(f"商品ID: {item_id}", "green"))
    print(color(f"理由: {reason}", "green"))
    print("=================\n")
    print(color("返金の実行に成功しました！", "green"))
    return "success"


def escalate_to_human(summary):
    """人間の担当者にエスカレーションする関数"""
    print(color("人間の担当者にエスカレーション中...", "red"))
    print("\n=== エスカレーションレポート ===")
    print(f"概要: {summary}")
    print("========================\n")
    exit()

# エージェントの初期設定
agent = Agent(
    name="Issues and Repairs Agent",
    instructions=(
        "あなたはACME Inc.のIssues and Repairs Agentです。"
        "常に1文以内で回答してください。"
        "まず自己紹介（会社名と役割）を行い、その後以下の手順でユーザーと対話してください:"
        "1. 最初に具体的な質問をして、ユーザーの問題を深く理解してください。\n"
        " - ただし、ユーザーが既に理由を提供している場合を除きます。\n"
        "2. 修正案を提案してください（適当なものを考え出してください）。試してもらいます。\n"
        "3. ユーザーが満足しない場合のみ、返金を提案してください。\n"
        "4. ユーザーが受け入れた場合、IDを検索して返金を実行してください。"
    ),
    tools=[execute_refund, look_up_item, escalate_to_human],
)

# メッセージ履歴を保存するリストを初期化
messages = []

# ユーザーとの対話を開始するループ
while True:
    # ユーザーの入力を取得
    user = input(color("User: ", "blue") + "\033[90m")
    messages.append({"role": "user", "content": user})  # ユーザーのメッセージを履歴に追加

    # 1回の対話を実行
    new_messages = run_full_turn(agent, messages)
    messages.extend(new_messages)
