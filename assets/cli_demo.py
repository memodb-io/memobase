import os
import platform
import shutil
from argparse import ArgumentParser
from datetime import datetime

from openai import OpenAI, AsyncOpenAI

from memobase import MemoBaseClient
from memobase.patch.openai import openai_memory

client: OpenAI | AsyncOpenAI
user_id: str
history: list

SYS_PROMPT_ZH = '''你是一个智能助手，目标是提供个性化、友好且有帮助的服务。请遵循以下原则：
1. **个性化**: 根据用户的兴趣和背景（如${user_interests}）提供建议，避免泄露隐私。
2. **友好互动**: 保持耐心、温暖的语气，让用户感到被尊重和支持。
3. **相关推荐**: 针对用户的兴趣（如美食、旅行等），适时分享有用的推荐或话题。
4. **避免重复**: 提供新信息或深入内容，避免重复用户已知的内容。
5. **灵活调整**: 根据用户反馈和对话上下文，动态调整回答风格。'''

SYS_PROMPT_EN = '''You are an intelligent assistant aiming to provide personalized, friendly, and helpful services. Please adhere to the following principles:
1. **Personalization**: Offer suggestions based on the user's interests and background (e.g., ${user_interests}), while avoiding privacy breaches.
2. **Friendly Interaction**: Maintain a patient and warm tone, making the user feel respected and supported.
3. **Relevant Recommendations**: Share useful recommendations or topics related to the user's interests (e.g., food, travel) at appropriate times.
4. **Avoid Repetition**: Provide new information or in-depth content, avoiding repetition of what the user already knows.
5. **Flexible Adjustment**: Dynamically adjust your response style based on user feedback and the context of the conversation.'''

SYS_PROMPT_JA = '''あなたは、パーソナライズされた、親しみやすく、役立つサービスを提供することを目的とした知的なアシスタントです。以下の原則を遵守してください:
1. **パーソナライゼーション**：ユーザーの興味や背景（例: ${user_interests}）に基づいて提案を行ってください。ただし、プライバシー侵害は避けてください。
2. **友好的な対話**: 忍耐強く温かい口調を保ち、ユーザーが尊重されサポートされていると感じられるようにしてください。
3. **関連性のある提案**: 適切なタイミングで、ユーザーの興味に関連する有益な提案や話題（例: 食物、旅行）を共有してください。
4. **繰り返しの回避**：ユーザーが既に知っている情報の繰り返しを避け、新しい情報や深い内容を提供してください。
5. **柔軟な調整**：ユーザーのフィードバックや会話の文脈に基づき、応答スタイルを動的に調整してください。'''

_WELCOME_MSG = """Welcome to Memobase, a user profile-based memory system. Type text to chat, :h for help.
(欢迎使用 Memobase，基于用户档案的记忆系统。输入内容开始对话，:h 获取帮助。)
(ユーザープロファイルベースのメモリシステム、Memobaseへようこそ。テキストを入力してチャット、:h でヘルプを表示。)"""
_HELP_MSG = """\
Commands:
    :help / :h              Show this help message   显示帮助信息             ヘルプを表示
    :exit / :quit / :q      Exit the demo            退出Demo                 デモを終了
    :clear / :cl            Clear screen             清屏                     ターミナルをクリア
    :clear-history / :clh   Clear history            清除对话历史             ヒストリーを表示
    :history / :his         Show history             显示对话历史             ヒストリーを表示
    :user                   Show user id             显示用户ID               ユーザIDを表示
    :user <id>              Set user id              设置用户ID               ユーザIDを設定
    :profile / :pf          Show user profile        显示用户已有的配置信息   ユーザのプロファイルを表示
    :flush / :fl            Flush buffer             刷新缓冲区               バッファをフラッシュ
"""
_ALL_COMMAND_NAMES = [
    "help",
    "h",
    "exit",
    "quit",
    "q",
    "clear",
    "cl",
    "clear-history",
    "clh",
    "history",
    "his",
    "user",
    "profile",
    "pf",
    "flush",
    "fl",
]

def _get_args():
    parser = ArgumentParser(description="OpenAI web chat demo.")
    parser.add_argument(
        "--openai-api-key",
        type=str,
        help="OpenAI API key",
    )
    parser.add_argument(
        "--openai-base-url",
        type=str,
        help="OpenAI API base url",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model name",
    )
    parser.add_argument(
        "--memobase-endpoint",
        type=str,
        default=os.getenv("MEMOBASE_ENDPOINT") or "http://localhost:8019",
        help="Memobase endpoint, default to environment variable MEMOBASE_ENDPOINT or %(default)r",
    )
    parser.add_argument(
        "--memobase-token",
        type=str,
        default=os.getenv("MEMOBASE_TOKEN") or "secret",
        help="Memobase token, default to environment variable MEMOBASE_TOKEN or %(default)r",
    )
    parser.add_argument(
        "--language", type=str, default='zh', help="Language, default to %(default)r"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="user_001",
        help="User ID, default to %(default)r",
    )
    args = parser.parse_args()
    if not args.openai_api_key:
        if os.getenv("OPENAI_API_KEY"):
            args.openai_api_key = os.getenv("OPENAI_API_KEY")
        else:
            print("You should set OPENAI_API_KEY environment variable or pass --openai-api-key argument.")
    if args.language == 'zh':
        args.sys_prompt = SYS_PROMPT_ZH
    elif args.language == 'ja':
        args.sys_prompt = SYS_PROMPT_JA
    else:
        args.sys_prompt = SYS_PROMPT_EN
    return args


def _setup_readline():
    try:
        import readline
    except ImportError:
        return

    _matches = []

    def _completer(text, state):
        nonlocal _matches

        if state == 0:
            _matches = [
                cmd_name for cmd_name in _ALL_COMMAND_NAMES if cmd_name.startswith(text)
            ]
        if 0 <= state < len(_matches):
            return _matches[state]
        return None

    readline.set_completer(_completer)
    readline.parse_and_bind("tab: complete")

def _clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def _print_history(history):
    terminal_width = shutil.get_terminal_size()[0]
    print(f"History ({len(history)})".center(terminal_width, "="))
    for message in history:
        print(f"{message['role']}: {message['content']}")
    print("=" * terminal_width)

def _get_input() -> str:
    while True:
        try:
            message = input("User> ").strip()
        except UnicodeDecodeError:
            print("[ERROR] Encoding error in input")
            continue
        except KeyboardInterrupt:
            exit(1)
        if message:
            return message
        else:
            pass
        # print("[ERROR] Query is empty")

def _process_command(query):
    global user_id, history
    command_words = query[1:].strip().split()
    if not command_words:
        command = ""
    else:
        command = command_words[0]

    if command in ["exit", "quit", "q"]:
        return False
    elif command in ["clear", "cl"]:
        _clear_screen()
        print(_WELCOME_MSG)
    elif command in ["clear-history", "clh"]:
        print(f"[INFO] All {len(history)} history cleared")
        history.clear()
    elif command in ["help", "h"]:
        print(_HELP_MSG)
    elif command in ["history", "his"]:
        _print_history(history)
    elif command in ["user"]:
        if len(command_words) == 1:
            print(f"[INFO] Current user id: {user_id}")
        else:
            user_id = command_words[1]
            print(f"[INFO] User id set to: {user_id}")
    elif command in ["profile", "pf"]:
        _print_profiles()
    elif command in ["flush", "fl"]:
        _flush()
    else:
        # error command
        print(f"[ERROR] Unknown command: {command}")
    return True

def _print_profiles():
    global client, user_id
    profiles = client.get_profile(user_id)
    user_profile_string = "\n".join(
        [f"- {p.topic}/{p.sub_topic}: {p.content}" for p in profiles]
    )
    print(f"[INFO] User profile: \n{user_profile_string}")

def _flush():
    global client, user_id
    client.flush(user_id)

def _chat_stream(model_name, sys_prompt, history):
    global client, user_id
    messages = history.copy()
    messages.insert(0, {"role": "system", "content": sys_prompt})
    messages[-1]['content'] = f"[{datetime.now()}]:{messages[-1]['content']}"
    stream = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=True,
        user_id=user_id
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def _launch_demo(args):
    global client, user_id, history

    client = OpenAI(
        api_key=args.openai_api_key,
        base_url=args.openai_base_url,
    )
    mb_client = MemoBaseClient(
        project_url=args.memobase_endpoint,
        api_key=args.memobase_token
    )
    client = openai_memory(client, mb_client)

    user_id = args.user_id
    history = []

    _setup_readline()
    _clear_screen()
    print(_WELCOME_MSG)

    while True:
        query = _get_input()
        if not query:
            continue
        # Process commands.
        if query.startswith(":"):
            if _process_command(query):
                continue
            else:
                break
        # Run chat.
        print(f"AI: ", end="")
        try:
            full_response = ""
            history.append({"role": "user", "content": query})
            for new_text in _chat_stream(args.model_name, args.sys_prompt, history):
                print(new_text, end="", flush=True)
                full_response += new_text
            print()
        except KeyboardInterrupt:
            print("[WARNING] Generation interrupted")
            continue
        history.append({"role": "assistant", "content": full_response})

def main():
    args = _get_args()
    _launch_demo(args)

if __name__ == "__main__":
    main()