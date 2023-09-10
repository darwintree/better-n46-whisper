import time
from typing import Any, Type, TypeVar

import openai
from pysubs2.ssafile import SSAFile

from better_n46_whisper.bundler.openai import OpenAiBundler
from better_n46_whisper.TYPES import Dialogue, DialogueWithTrans, Segment, PromptMessage

T = TypeVar("T")


def split_array(arr: list[T], max_length: int) -> list[list[T]]:
    # 初始化一个空列表用于存储子数组
    sub_arrays = []

    # 获取数组的长度
    arr_length = len(arr)

    # 计算需要多少个子数组
    num_sub_arrays = (arr_length + max_length - 1) // max_length

    # 切割数组并存储到 sub_arrays 列表中
    for i in range(num_sub_arrays):
        start_index = i * max_length
        end_index = (i + 1) * max_length
        sub_array = arr[start_index:end_index]
        sub_arrays.append(sub_array)

    return sub_arrays


# input --bundle-> translate --debundle-> output

default_prompt = """
**Transcription Translation to Simplified Chinese**

**Objective**: Provide Simplified Chinese translation for the transcribed texts, ensuring accuracy, context-awareness, and conciseness.

**Input Format**:
- Multiple lines.
- Each line: `[index]|[speaker]|[text]`.
- Transcribed from an audio file, may contain inaccuracies.

**Output Format**:
- Multiple lines.
- Each line: `[index]|[speaker]|[text]|[translation]`. 
- **IMPORTANT**: The `[index]|[speaker]|[text]` MUST be an exact copy of the corresponding input line. The translation is appended to the tail of the line as the `[translation]` part. **DO NOT REPLACE OR OMIT THE ORIGINAL TEXT**.

**Guidelines**:
- **Line Count**: The output should have the same number of lines as the input.
- **Contextual Accuracy**: Correct potential transcription mistakes using context.
- **Fluency**: Translations should sound natural to native Simplified Chinese speakers.
- **Conciseness**: Ensure translations are concise without sacrificing meaning or clarity.
- **Format**: **Always retain the original text** in the output and add the translation in the new segment.

**Example**:
Input: 
```
0|佐藤|おはようございます！
1|櫻木|おはようございます！
```
Output: 
```
0|佐藤|おはようございます！|早上好！
1|櫻木|おはようございます！|早上好！
```
"""


# '''
# Instructions:
#   You are tasked with translating transcribed text into Simplified Chinese. As a language expert, ensure accuracy, context-awareness, and fluency in your translations.

# Details:
#   - The user's input will be structured in multiple lines. Each line follows this format: `[index]|[speaker]|[text]`.
#   - The text is transcribed from an audio file and may contain errors or inaccuracies.

# Guidelines:
#   - While there doesn't need to be a strict one-to-one correspondence between the lines before and after translation, **it is imperative that the total number of output lines matches the total number of input lines**.
#   - Use the surrounding context to deduce and correct potential transcription mistakes.
#   - Ensure that the translated text is not only accurate but also fluent and natural to native Simplified Chinese speakers.
#   - Maintain the original format of the input. Only the '[text]' segment should be replaced with its translated Simplified Chinese counterpart.

# Note:
#   The total count of lines in the output should be the same as the input, even if the content of individual lines may vary.
# '''


class LLMTranslator:
    def __init__(
        self,
        key,
        model="gpt-3.5-turbo",
        prompt=default_prompt,
        temperature=0.7,
        api_base=None,
        Bundler: Type[OpenAiBundler] = OpenAiBundler,
    ):
        self.key = key
        # self.keys = itertools.cycle(key.split(","))
        # self.language = language
        # self.key_len = len(key.split(","))
        self.bundler = Bundler(None)
        self.temperature = temperature
        self.model = model
        if not api_base:
            openai.api_base = api_base
        # openai.api_key = key

    # def rotate_key(self):
    #     openai.api_key = next(self.keys)
    
    def chat(self, prompt_messages: list[PromptMessage], retry=1) -> tuple[str, int]:
        openai.api_key = self.key
        try:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=prompt_messages,
                temperature=self.temperature,
            )
            t_text: str = (
                completion["choices"][0] # type: ignore
                .get("message")
                .get("content")
                .encode("utf8")
                .decode()
            )
            total_tokens: int = completion["usage"][ # type: ignore
                "total_tokens"
            ]  # include prompt_tokens and completion_tokens
            return t_text, total_tokens
        except Exception as e:
            if retry <= 0:
                raise e
            # TIME LIMIT for open api , pay to reduce the waiting time
            sleep_time = 1
            time.sleep(sleep_time)
            print(e, f"will sleep  {sleep_time} seconds")
            return self.chat(prompt_messages, retry=retry - 1)
    
    ## TODO: async translate
    def translate(
        self, input: list[Dialogue], retry=1
    ) -> tuple[list[DialogueWithTrans], int]:
        try:
            t_text, total_tokens = self.chat(self.bundler.bundle_input(input), retry)
        except Exception as e:
            print(e)
            t_text, total_tokens = "", 0
        output = self.bundler.debundle_ouput(t_text)
        return self.bundler.integrate_in_and_out(input, output), total_tokens

    def divide_and_translate(
        self, input: list[Dialogue], retry=1, batch_size=30
    ) -> tuple[list[DialogueWithTrans], int]:
        sub_arrays = split_array(input, batch_size)
        translated_results = []
        consumed_token = 0
        for array in sub_arrays:
            out, new_token = self.translate(array, retry)
            translated_results += out
            consumed_token += new_token
        return translated_results, consumed_token

    # TODO: switch to a better implementation
    # TODO: the current implementation makes it hard to adjust subtitle style
    def translate_ass(self, file: SSAFile, retry=1, batch_size=30):
        dialogues: list[Dialogue] = []
        for i in range(len(file)):
            dialogues.append(
                {"index": i, "speaker": file[i].style, "text": file[i].text}
            )
        output, consumed_token = self.divide_and_translate(
            dialogues, retry=retry, batch_size=batch_size
        )
        for i in range(len(file)):
            translation = output[i]["trans"]
            if len(translation) > 35:
                translation = (
                    translation[: len(translation) // 2]
                    + "\\N"
                    + translation[len(translation) // 2 :]
                )
            file[i].text = f"{file[i].text}\\N{translation}"
        print("consumed token in all: ", consumed_token)
