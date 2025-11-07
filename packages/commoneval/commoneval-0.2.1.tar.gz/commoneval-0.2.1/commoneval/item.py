"""Define Item classes for LLM evaluation benchmarks.

An Item is a single pairing of response and prompt for LLM evaluation, along with other metadata.
Items come in different types depending on the expected response modality.

## Item Types

- **BooleanItem**: For true/false questions
- **TernaryItem**: For true/false/unknown questions
- **ClosedSetItem**: For multiple-choice questions (2-5 choices)
- **OpenEndedItem**: For open-ended text responses

>>> from commoneval.item import BooleanItem, TernaryItem, ClosedSetItem, OpenEndedItem, Modality, Ternary
>>> boolitem = BooleanItem(identifier="bool.1", modality=Modality.BOOLEAN, prompt="Is the sky blue?", response=True,)
>>> ternitem = TernaryItem(identifier="tern.1", modality=Modality.TERNARY, prompt="Is there life on Mars?", response=Ternary.UNKNOWN)
>>> mcqitem = ClosedSetItem(identifier="mcq.1", modality=Modality.CHOICEOF4, prompt="What is the capital of France?", response=1, choices=["London", "Paris", "Berlin", "Madrid"],)
>>> openitem = OpenEndedItem(identifier="cloze.1", modality=Modality.CLOZE, prompt="The capital of France is ___.", response="Paris",)
>>> singleitem = OpenEndedItem(identifier="single.1", modality=Modality.SINGLEVALUE, prompt="What is 2 + 2?", response="4",)
>>> shortitem = OpenEndedItem(identifier="short.1", modality=Modality.SHORTPROSE, prompt="Name a primary color.", response="Red",)
>>> longitem = OpenEndedItem(identifier="long.1", modality=Modality.LONGPROSE, prompt="Describe the water cycle.", response="The water cycle consists of evaporation, ...",)

## Serialization

All items can be serialized to dictionaries and JSONL format:

```python
# Convert to dictionary
item_dict = item.as_dict()

# Write to JSONL file
with open("items.jsonl", "w") as f:
    item.write_jsonline(f)
```

See tests/commoneval/test_item.py for more examples.
"""

from dataclasses import dataclass, field
import json
import re
import sys
from typing import Any, IO, Type
from warnings import warn

try:
    from enum import StrEnum  # Available in Python 3.11+
except ImportError:
    # Fallback for Python < 3.11
    from enum import Enum

    class StrEnum(str, Enum):
        pass


# deal with version differencs for StrEnum value checking
def is_valid_enum_value(value: str, enum_class: Type[StrEnum]) -> bool:
    """Check if a value is a valid member of an enum class."""
    if sys.version_info >= (3, 12):
        # Python 3.12+ allows direct containment
        return value in enum_class
    else:
        # Python 3.11 and earlier require manual check
        return value in enum_class._value2member_map_


# enumerate values for moddality
class Modality(StrEnum):
    """Enumerates the types of responses that the prompt expects."""

    # closed-set responses
    #
    BOOLEAN = "boolean"
    CHOICEOF2 = "choiceof2"
    CHOICEOF3 = "choiceof3"
    CHOICEOF4 = "choiceof4"
    CHOICEOF5 = "choiceof5"
    TERNARY = "ternary"
    # open-ended responses
    CLOZE = "cloze"
    SINGLEVALUE = "singlevalue"
    SHORTPROSE = "shortprose"
    LONGPROSE = "longprose"


class Ternary(StrEnum):
    """Enumerate strings representing boolean values plus 'Unknown'."""

    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


@dataclass(repr=False)
class BaseItem:
    """Base class for Items - a single pairing of response and prompt for LLM evaluation, along with other metadata."""

    # The ID of the item
    identifier: str
    # identifies the type of response that the prompt expects
    modality: Modality
    # The prompt used to generate the response
    prompt: str
    # subclasses define the type of response more specifically
    #
    # optional values below here
    # Content that justifies the reference answer
    support: str = ""
    # Directions for how the LLM should respond to the prompt
    taskPrompt: str = ""
    # The difficulty of the item, from 0.0 to 1.0
    difficulty: float = 0.0
    # stash other data here if needed
    otherargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization checks for the BaseItem class."""
        # BaseItem should not be instantiated directly
        if type(self) is BaseItem:
            raise TypeError(
                "BaseItem cannot be instantiated directly. "
                "Use BooleanItem, TernaryItem, ClosedSetItem, or OpenEndedItem instead."
            )

        assert re.fullmatch(
            r"[-a-zA-Z0-9_.]+", self.identifier
        ), f"Identifier {self.identifier} has invalid characters."
        # response is defined on subclasses but is required
        assert hasattr(self, "response"), "Response attribute is missing."
        # Check for empty string responses (only applies to subclasses with string responses)
        if (
            self.modality != Modality.BOOLEAN
            and isinstance(self.response, str)
            and len(self.response) == 0
        ):
            warn("Response is empty.")
        assert 1.0 >= self.difficulty >= 0.0, "Difficulty must be between 0.0 and 1.0."

    def __repr__(self) -> str:
        """Return a string representation of the Item."""
        # Truncate prompt if too long
        if len(self.prompt) > 20:
            promptstr = self.prompt[:17] + "..."
        else:
            promptstr = self.prompt

        # Handle response representation (may be in subclass)
        if isinstance(self.response, str) and len(self.response) > 20:
            responsestr = self.response[:17] + "..."
        else:
            responsestr = self.response

        return f"<{self.__class__.__name__}({self.identifier!r}, {self.modality}): {promptstr!r}->{responsestr!r}>"

    def as_dict(self) -> dict[str, Any]:
        """Return the Item as a dictionary for serialization."""
        outdict = {
            "identifier": self.identifier,
            "prompt": self.prompt,
            "response": self.response,
            "modality": self.modality.value,
        }
        if self.taskPrompt:
            outdict["taskPrompt"] = self.taskPrompt
        if self.support:
            outdict["support"] = self.support
        if self.otherargs:
            # this assumes no collisions with existing keys and that
            # values are JSON-serializable
            outdict["otherargs"] = self.otherargs
        return outdict

    def write_jsonline(self, fp: IO[str]) -> str:
        """Return the Item as a JSONL string."""
        json.dump(self.as_dict(), fp)
        fp.write("\n")


@dataclass(repr=False, kw_only=True)
class BooleanItem(BaseItem):
    """Item subclass for BOOLEAN modality."""

    # The expected 'gold standard' response: LLM output is compared to this
    response: bool

    def __post_init__(self):
        """Post-initialization checks for BooleanItem."""
        super().__post_init__()

        if self.modality != Modality.BOOLEAN:
            raise ValueError(
                f"BooleanItem requires BOOLEAN modality, got {self.modality}"
            )

        assert self.response in {
            True,
            False,
        }, "Response is not a valid boolean."


@dataclass(repr=False, kw_only=True)
class TernaryItem(BaseItem):
    """Item subclass for TERNARY modality."""

    # The expected 'gold standard' response: LLM output is compared to this
    response: Ternary

    def __post_init__(self):
        """Post-initialization checks for TernaryItem."""
        super().__post_init__()

        if self.modality != Modality.TERNARY:
            raise ValueError(
                f"TernaryItem requires TERNARY modality, got {self.modality}"
            )

        assert is_valid_enum_value(
            self.response, Ternary
        ), "Response is not a valid ternary value."


# future: specifying both a Modality and a list of choices is
# redundant. Can we just do one?
@dataclass(repr=False, kw_only=True)
class ClosedSetItem(BaseItem):
    """Item subclass for multiple-choice responses (CHOICEOF2-5).

    The number of choices must match the modality. The response must
    be an integer index (zero-based) into the choices list, and must
    indicate the correct answer.

    """

    # The expected 'gold standard' response: LLM output is compared to this
    response: int
    choices: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization checks for ClosedSetItem."""
        super().__post_init__()
        assert (
            self.response >= 0
        ), f"Response index {self.response} must be non-negative."
        assert self.response < len(
            self.choices
        ), f"Response index {self.response} out of range."
        assert len(self.choices) >= 2, "There must be at least 2 choices."
        assert len(self.choices) <= 5, "There can be at most 5 choices."
        match len(self.choices):
            case 2:
                assert (
                    self.modality == Modality.CHOICEOF2
                ), "Modality does not match 2 choices."
            case 3:
                assert (
                    self.modality == Modality.CHOICEOF3
                ), "Modality does not match 3 choices."
            case 4:
                assert (
                    self.modality == Modality.CHOICEOF4
                ), "Modality does not match 4 choices."
            case 5:
                assert (
                    self.modality == Modality.CHOICEOF5
                ), "Modality does not match 5 choices."

    # ToDo: add a randomize parameter to shuffle choices
    def as_dict(self, style: str = "letter") -> dict[str, Any]:
        """Return the ClosedSetItem as a dictionary for serialization.

        Formats the choices according to the specified style for the
        response value, and modified the response to the corresponding
        index from choices. Adds a taskPrompt value for the available
        choices.

        """
        outdict = super().as_dict()
        # only letter for now
        assert style in ("letter"), f"Invalid style {style!r}, must be 'letter'."
        choicedict = dict(zip(["A", "B", "C", "D", "E"], self.choices))
        formatted: str = " ".join(
            [f"{letter}) {val}" for (letter, val) in choicedict.items()]
        )
        choiceletters: list[str] = list(choicedict.keys())
        choices_prefix: str = (
            ", ".join(choiceletters[:-1]) + f", or {choiceletters[-1]}"
        )
        outdict["taskPrompt"] = (
            f"Choose one of the following {len(self.choices)} options: {formatted}. Return only the single letter corresponding to your choice, one of {choices_prefix}."
        )
        outdict["response"] = choiceletters[self.response]
        if "otherargs" not in outdict:
            outdict["otherargs"] = {}
        outdict["otherargs"]["choices"] = self.choices
        return outdict


@dataclass(repr=False, kw_only=True)
class OpenEndedItem(BaseItem):
    """Item subclass for open-ended responses (CLOZE, SINGLEVALUE, SHORTPROSE, LONGPROSE)."""

    # The expected 'gold standard' response: LLM output is compared to this
    response: str

    def __post_init__(self):
        """Post-initialization checks for OpenEndedItem."""
        super().__post_init__()

        match self.modality:
            case Modality.CLOZE:
                assert "___" in self.prompt, "Prompt is missing ___ cloze indicator."
            case Modality.SINGLEVALUE | Modality.SHORTPROSE | Modality.LONGPROSE:
                # No additional validation for these modalities
                pass
            case _:
                raise ValueError(
                    f"Modality {self.modality} is not an open-ended modality."
                )


# Need a subclass for multiple responses: assume for base Item that there's a single response
# need to think through lists or dicts for responses


# Subclass of BaseItem for templated items
# THIS NEEDS WORK: parking code here for now
@dataclass(repr=False)
class TemplatedItem(BaseItem):
    """A subclass of BaseItem for templated items."""

    # if the prompt is templated, the values for instantiating the template
    promptVariables: dict[str, str] = field(default_factory=dict)
    # if the prompt is templated, the values for the responses
    responseVariables: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post-initialization checks for the TemplatedItem class."""
        super().__post_init__()
        # check that the prompt variables are valid
        for key in self.promptVariables:
            assert key in self.get_template_keys(), f"Invalid prompt variable {key}."
        # check that the response variables are valid
        for key in self.responseVariables:
            assert key in self.get_template_keys(), f"Invalid response variable {key}."
        if "{" in self.prompt:
            assert self.isTemplated, "Prompt is templated but isTemplated is False"
            assert len(self.get_template_keys()) == len(
                self.response
            ), "Prompt is templated but number of keys does not match number of responses"
            assert bool(
                self.promptVariables
            ), "Prompt is templated but no prompt variables provided"
            assert bool(
                self.responseVariables
            ), "Prompt is templated but no response variables provided"

    def get_template_keys(self) -> set[str]:
        """If the prompt is templated, return the keys in the template.

        This identifies brackets in the string, ensures they are
        correctly paired and not empty, and returns the set of
        keys. Any duplicate keys will be treated the same.

        If the prompt is not templated, return an empty set.

        """
        if not self.isTemplated:
            return set()
        else:
            keys = set()
            stack = []
            for i, c in enumerate(self.prompt):
                if c == "{":
                    stack.append(i)
                elif c == "}":
                    if not stack:
                        raise ValueError(f"Unmatched '}}' at index {i} in prompt.")
                    start = stack.pop()
                    key = self.prompt[start + 1 : i]
                    if not key:
                        raise ValueError(
                            f"Empty key in prompt at indices {start} to {i}."
                        )
                    keys.add(key)
            if stack:
                raise ValueError(f"Unmatched '{{' at indices {stack} in prompt.")
            return keys

    def generate_prompts(self) -> list[str]:
        """Generate the prompts from the template and the variables."""
        return [
            self.prompt.replace("{" + key + "}", value)
            for index, key in list(enumerate(self.get_template_keys()))
            for value in self.promptVariables[key]
        ]
