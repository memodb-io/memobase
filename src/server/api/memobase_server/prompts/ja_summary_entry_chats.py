from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "ja_summary_entry_chats",
}
SUMMARY_PROMPT = """あなたは、チャットから個人情報、スケジュール、イベントを記録する専門家です。
あなたには、ユーザーとアシスタント間で行われたチャットが与えられます。

## 要件
- すべての可能なユーザー情報、スケジュール、イベントをリストアップする必要があります
- {additional_requirements}
- ユーザーのイベント/スケジュールに特定の言及日時またはイベント発生日時が含まれている場合、メッセージ内の日時情報を変換して、記録の後の[TIME]内にメッセージ内のイベント日付情報を変換してください。例えば:
    入力: `[2024/04/30] user: 昨日、新車を買ったんだ！`
    出力: `ユーザは新車を購入した。[2024/04/30に言及、2024/04/29に車購入]。`
    入力: `[2024/04/30] user: 4年前に車を買ったんだ！`
    出力: `ユーザは車を購入した。[2024/04/30に言及、2020年に車購入]。`
    説明: 正確な日付はわからず、年のみが判明している。したがって2024-4=2020となる。または[2024/04/30の4年前]と記録することも可能。
    入力: `[2024/04/30] user: 先週、新車を買ったんだ！`
    出力: `ユーザは新車を購入した。[2024/04/30に言及、2024/04/30の1週前に車購入]。`
    説明: 正確な日付がわからないため。
    入力: `[...] user: 先週、新車を買ったんだ！`
    出力: `ユーザは新車を購入した。`
    説明: 正確な日付がわからないため、日付を含めない。

### 重要情報
以下は、チャットから記録すべきトピック/サブトピックです。
<topics>
{topics}
</topics>
以下は、チャットから記録すべき重要な属性です。
<attributes>
{attributes}
</attributes>

## 入力フォーマット
### すでに記録済み
過去の記録結果のリストを受け取ります。既に記録されている情報に関連する可能性のある関連情報も記録してください。
過去の結果はプロファイル形式で整理されています:
- TOPIC{separator}SUBTOPIC{separator}CONTENT... // maybe truncated

### 入力されるチャット
ユーザーとアシスタントの会話を受け取ります。会話の形式は以下の通りです:
- [TIME] NAME: MESSAGE
ここでは、NAMEはALIAS(ROLE)または単にROLEです。ALIASが利用可能な場合は、ユーザー/アシスタントを指すのにALIASを使用してください。
MESSAGEは会話の内容です。
TIMEはメッセージが発生した時刻です。必要に応じて、メッセージ内の日付情報をTIMEに基づいて変換してください。

## 出力フォーマット
- LOGGING[TIME INFO] // TYPE
記録結果をMarkdownの箇条書き形式で出力してください。
例えば:
```
- Jackが子供たちの絵を描いた。[2023/01/23に言及] // event
- ユーザーの別名はJack、アシスタントはMelinda。 // info
- Jackは自身の職業がMemobaseのソフトウェアエンジニアだと述べた。[2023/01/23に言及] // info
- Jackはジムに行く予定。[2023/1/23に言及、2023/01/24にジムに行く予定] // schedule
...
```
記録には必ず具体的な言及日時を、可能であればイベント発生日時も追加してください。
記録は純粋かつ簡潔に保ってください。日時情報は全て[TIME INFO]ブロック内に移動させてください。

## コンテンツ要求
- すべての可能なユーザー情報、スケジュール、イベントをリストアップする必要があります
- {additional_requirements}

では、作業を実行してください。
"""


def pack_input(already_logged_str: str, chat_strs: str):
    return f"""### 既に記録済み
{already_logged_str}

### 入力されるチャット
{chat_strs}
"""


def get_prompt(
    topic_examples: str, attribute_examples: str, additional_requirements: str = ""
) -> str:
    return SUMMARY_PROMPT.format(
        topics=topic_examples,
        attributes=attribute_examples,
        additional_requirements=additional_requirements,
        separator=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
