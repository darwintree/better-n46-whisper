from typing import List

from better_n46_whisper.TYPES import Dialogue, PromptMessage

from .base import Bundler

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

# input --bundle-> translate --debundle-> output
class OpenAiBundler(Bundler):
    
    _default_prompt = default_prompt

    def serialize_input(self, input: List[Dialogue]) -> str:
        """
        Serializes a list of dialogues into a string format.
        Each dialogue is represented as "index|speaker|text".

        :param List[Dialogue] input
        :return str
        """
        result = ""
        for i, dialogue in enumerate(input):
            result += f"{i}|{dialogue['speaker']}|{dialogue['text']}\n"
        return result
    
    def bundle_input(self, input: List[Dialogue]) -> List[PromptMessage]:
        return [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": self.serialize_input(input)},
        ]
    
    def debundle_ouput(self, choice: str) -> dict[int, str]:
        rtn: dict[int, str] = {}
        for line in choice.replace("\r\n", "\n").split("\n"):
            try:
                text = line.split("|")[-1]
                index = int(line.split("|")[0])
                rtn[index] = text
            except Exception:
                continue
        return rtn
