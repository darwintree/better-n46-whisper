from typing import TypedDict, List, Literal, Any, Union

class Dialogue(TypedDict):
    """
    The basic input unit.
    index: the unique index of a sentence within a bundle
    speaker: the tag of the sentence
    text: the content of the sentence
    """
    index: int
    speaker: str
    text: str

class DialogueWithTrans(Dialogue):
    trans: str
    
class PromptMessage(TypedDict):
    role: Literal["system", "assistant", "user"]
    content: str

class Segment(TypedDict):
    start: float
    end: float
    text: str
    words: Any
    speaker: Union[None, str]
