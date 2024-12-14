from openai import OpenAI
from demo_util import color, function_to_schema
import json
from pydantic import BaseModel

# === クラス定義 ===

class Agent(BaseModel):
    """エージェントを定義するクラス。
    name: エージェント名
    model: 使用するモデル名
    instructions: システムメッセージとしてエージェントの振る舞いを定義
    tools: 使用可能なツールのリスト"""
    name: str = "Agent"
    model: str = "gpt-4o"
    instructions: str = "You are a helpful Agent"
    tools: list = []

class Response(BaseModel):
    """レスポンスメッセージを管理するクラス。"""
    messages: list

# OpenAI クライアントの初期化
client = OpenAI()

# === デモループ ===

def run_full_turn(agent, messages):
    """エージェントとの1ターンの対話を処理します。

    Args:
        agent (Agent): エージェントの設定を含むオブジェクト。
        messages (list): ユーザーとエージェントの間のメッセージリスト。

    Returns:
        list: 新しく追加されたメッセージ。"""

    num_init_messages = len(messages)
    messages = messages.copy()

    while True:

        # ツールをスキーマに変換し、逆引きマップを保存
        tool_schemas = [function_to_schema(tool) for tool in agent.tools]
        tools_map = {tool.__name__: tool for tool in agent.tools}

        # === 1. OpenAI のコンプリートを取得 ===
        response = client.chat.completions.create(
            model=agent.model,
            messages=[{"role": "system", "content": agent.instructions}] + messages,
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
    """指定されたツール呼び出しを実行します。

    Args:
        tool_call (dict): 呼び出すツールの詳細。
        tools_map (dict): ツール名と関数のマッピング。

    Returns:
        any: ツールの実行結果。"""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(color("Assistant:", "yellow"), color(f"{name}({args})", "magenta"))

    # 指定された引数で対応する関数を呼び出す
    return tools_map[name](**args)

# === ツール関数 ===

def look_up_item(search_query):
    """商品IDを見つけるために使用します。
    検索クエリには説明やキーワードを使用できます。

    Args:
        search_query (str): 検索クエリ。

    Returns:
        str: 商品ID。"""
    item_id = "item_132612938"
    print(color("見つかった商品:", "green"), item_id)
    return item_id

def execute_refund(item_id, reason="not provided"):
    """指定された商品IDと理由を元に返金処理を実行します。

    Args:
        item_id (str): 商品ID。
        reason (str, optional): 返金理由。デフォルトは "not provided"。

    Returns:
        str: 処理結果。"""
    print(color("\n\n=== 返金概要 ===", "green"))
    print(color(f"商品ID: {item_id}", "green"))
    print(color(f"理由: {reason}", "green"))
    print("=================\n")
    print(color("返金の実行に成功しました！", "green"))
    return "success"

def escalate_to_human(summary):
    """明示的にリクエストされた場合のみ、この関数を呼び出します。

    Args:
        summary (str): エスカレーションの概要。

    Exits:
        プログラムを終了。"""
    print(color("人間の担当者にエスカレーション中...", "red"))
    print("\n=== エスカレーションレポート ===")
    print(f"概要: {summary}")
    print("========================\n")
    exit()

# === エージェントの設定 ===

agent = Agent(
    name="Issues and Repairs Agent",
    instructions=(
        "あなたはACME Inc.の問題解決と修理の担当者です。"
        "常に1文以内で回答してください。"
        "まず自己紹介（会社と役割）を行い、以下の手順に従ってください:"
        "1. 最初に具体的で深掘りする質問を行い、ユーザーの問題をより深く理解してください。\n"
        " - ただし、ユーザーが既に理由を提供している場合を除きます。\n"
        "2. 修正案を提案してください（適当なものを考え出してください）。ユーザーが試すまで待ちます。\n"
        "3. ユーザーが満足しない場合のみ、返金を提案してください。\n"
        "4. ユーザーが受け入れた場合、IDを検索して返金を実行してください。"
    ),
    tools=[execute_refund, look_up_item, escalate_to_human],
)

# 会話メッセージの初期化
messages = []

# ユーザーと継続的に対話するループを開始
while True:
    # ユーザー入力を取得
    user = input(color("User: ", "blue") + "\033[90m")
    messages.append({"role": "user", "content": user})

    # 新しいやり取りを実行
    new_messages = run_full_turn(agent, messages)
    messages.extend(new_messages)
