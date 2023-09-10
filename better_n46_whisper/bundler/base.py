import abc
from typing import List, Union

from better_n46_whisper.TYPES import Dialogue, DialogueWithTrans, PromptMessage

class Bundler(abc.ABC):
    """
    The Bundler class is an abstract base class that provides methods for serializing and deserializing
    dialogue data, as well as integrating input and output data. The main purpose of this class is to
    bundle input data, send it for translation, and then debundle the translated output.
    """
    
    _default_prompt = ""
    
    # Constructor initializes the Bundler with a given prompt.
    def __init__(self, propmt: Union[str, None]):
        if propmt is None:
            self.prompt = self._default_prompt
        else:
            self.prompt = propmt
    
    @abc.abstractmethod
    def bundle_input(self, input: List[Dialogue]) -> List[PromptMessage]:
        """
        Bundles the input dialogues into a format suitable for translation. 
        This method must be overridden by subclasses.

        :param List[Dialogue] input: List of dialogues to be bundled.
        :return List[PromptMessage]: bundled messages ready as LLM input.
        """

    # Deserializes the output string into a dictionary format.
    # The dictionary maps relative indices to their corresponding translations.
    @abc.abstractmethod
    def debundle_ouput(self, choice: str) -> dict[int, str]:
        """
        Converts the translated output string back into a dictionary format.
        The dictionary maps relative indices to their respective translations.

        :param str choice: The serialized string of translated dialogues.
        :return dict[int, str]: Dictionary mapping indices to translations.
        """


    def before_integration(self, input: List[Dialogue], output: dict[int, str]) -> None:
        """
        Prepares the output translations to align with the input dialogues.
        This method can be overridden by subclasses for custom alignment strategies.

        :param List[Dialogue] input: Original list of dialogues.
        :param dict[int, str] output: Dictionary of translated dialogues.
        """
        # an easy implementation
        pass

    def integrate_in_and_out(
        self, input: List[Dialogue], output: dict[int, str]
    ) -> List[DialogueWithTrans]:
        """
        Merges the input dialogues with their corresponding translations.
        Returns a list of dialogues paired with their translations.

        :param List[Dialogue] input: Original list of dialogues.
        :param dict[int, str] output: Dictionary of translated dialogues.
        :return List[DialogueWithTrans]: List of dialogues with their translations.
        """
        self.before_integration(input, output)
        result: List[DialogueWithTrans] = []
        for i, dialogue in enumerate(input):
            if output.get(i, "") == "":
                print(f"missed: {dialogue['index']} - {dialogue['text']}")
            result.append({**dialogue, "trans": output.get(i, "")})
        return result
