"""Given a list of questions and answers, output JSONL for Items.

This is for bootstrapping benchmarks from existing data.

Example usage:
>>> from commoneval import ROOT, makeitems
>>> questions = ["What does the Bible say is God’s purpose for my life?",
  "Who am I in Christ, and how does that shape my identity?",
  "How do I find meaning in Christ apart from my accomplishments?",]
>>> destpath = ROOT.parent / "eval-Larson/data/eng/larson-commonchristian"
>>> writer = makeitems.QuestionWriter(questions=questions,
  identifier_prefix="lcc", outpath=destpath / f"{destpath.name}.jsonl")

"""

from collections import UserDict
from pathlib import Path

import unicodecsv

import item


class QuestionWriter:
    """Write items to a JSONL file.

    This assumes you have questions (prompts) but no answers (responses).
    """

    def __init__(
        self,
        questions: list[str],
        identifier_prefix: str,
        outpath: Path,
        modality: item.Modality = item.Modality.LONGPROSE,
    ) -> None:
        """Initialize the writer."""
        self.id_index: int = 0
        with outpath.open("w", encoding="utf-8") as f:
            for question in questions:
                itm = item.OpenEndedItem(
                    identifier=f"{identifier_prefix}{self.id_index:04d}",
                    prompt=question,
                    modality=modality,
                    response="",
                )
                itm.write_jsonline(f)
                self.id_index += 1


class SubjectQuestionWriter:
    """Write items to a JSONL file.

    This assumes you have pairs of questions (prompts) with subjects,
    but no answers (responses).

    """

    def __init__(
        self,
        items: list[str],
        identifier_prefix: str,
        outpath: Path,
        modality: item.Modality = item.Modality.LONGPROSE,
    ) -> None:
        """Initialize the writer."""
        self.id_index: int = 0
        with outpath.open("w", encoding="utf-8") as f:
            for subject, question in items:
                itm = item.OpenEndedItem(
                    identifier=f"{identifier_prefix}{self.id_index:04d}",
                    prompt=question,
                    modality=modality,
                    response="",
                    otherargs={"subject": subject},
                )
                itm.write_jsonline(f)
                self.id_index += 1


class CSVMCQuestionWriter(UserDict):
    """Read multiple questions from CSV and write items to a JSONL file.

    Assumes some standard column headers and 4 answer choices.

    """

    # this will depend on the CSV format
    header_map: dict[str, str] = {
        "Question_Number": "identifier",
        "Question_Text": "prompt",
        "Option_A": "0",
        "Option_B": "1",
        "Option_C": "2",
        "Option_D": "3",
        "Correct_Answer": "response",
    }
    other_fields_map: dict[str, str] = {
        "Religious_Tradition": "Religious_Tradition",
        "Score": "Score",
        "Feedback": "Feedback",
    }
    letter_answers: tuple[str, ...] = ("A", "B", "C", "D")

    def __init__(
        self,
        inpath: Path,
        outpath: Path,
        modality: item.Modality = item.Modality.CHOICEOF4,
    ) -> None:
        """Initialize the writer."""
        super().__init__()
        with inpath.open("rb") as f:
            reader = unicodecsv.DictReader(f)
            self.rowitems = [row for row in reader]
        with outpath.open("w", encoding="utf-8") as f:
            for itemdict in self.rowitems:
                # print(itemdict["correct_answer"])
                # choices = {itemdict[letter] for letter in ["A", "B", "C", "D"]}
                # print(choices)
                try:
                    # this assumes single letters, with A = first choice
                    # and computes the offset from there
                    assert (
                        itemdict["Correct_Answer"] in self.letter_answers
                    ), f"Expected letter answer: {itemdict['Correct_Answer']}"
                    ans_index = ord(itemdict["Correct_Answer"].lower()) - ord("a")
                except ValueError:
                    raise ValueError(
                        f"correct_answer must resolve to an int: got {itemdict['Correct_Answer']}."
                    )
                itemargs = {
                    # identifier
                    self.header_map["Question_Number"]: itemdict["Question_Number"],
                    "modality": modality,
                    # prompt
                    self.header_map["Question_Text"]: itemdict["Question_Text"],
                    # response
                    self.header_map["Correct_Answer"]: ans_index,
                    "choices": [
                        itemdict[choice]
                        for choice in ["Option_A", "Option_B", "Option_C", "Option_D"]
                    ],
                }
                for field, key in self.other_fields_map.items():
                    if "otherargs" not in itemargs:
                        itemargs["otherargs"]: dict[str, str] = {}
                    if field in itemdict:
                        itemargs["otherargs"][key] = itemdict[field]
                itm = item.ClosedSetItem(**itemargs)
                self.data[itm.identifier] = itm
                itm.write_jsonline(f)
