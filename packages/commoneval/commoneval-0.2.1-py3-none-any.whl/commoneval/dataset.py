"""Define the Dataset class

A Dataset is a collection of Item instances, each with a unique identifier,
prompt, response, etc.

>>> from commoneval import dataset, DATAPATH
# create one manually: not the typical case
>>> from datetime import date
>>> ds = dataset.Dataset("a3d", created=date.today(), creator="Biblica", description="A test",
         source="head", subject="test", hasPart=["a3d_000.jsonl", "a3d_001.jsonl"])
>>> ds
<Dataset(a3d, test)>
>>> ds.asdict()
{'identifier': 'a3d', 'contributor': None, 'created': '2025-05-09', 'creator': 'Biblica', 'datePublished': None, 'description': 'A test', 'hasPart': ['a3d_000.jsonl', 'a3d_001.jsonl'], 'language': 'eng', 'license': 'CC-BY-NC-SA-4.0', 'publisher': None, 'source': 'head', 'sourceProcess': '', 'subject': 'test', 'taskPrompt': '', 'title': '', 'version': '1.0'}

# write to file
>>> with (DATAPATH / "a3d.yaml").open("w") as fp:
...   ds.write_yaml(fp)

# read a dataset from a file: this is the typical case
>>> with (DATAPATH / "a3d.yaml").open() as fp:
...   ds2 = dataset.Dataset.read_yaml(fp)
>>> ds2 == ds
True
# read items into a dataset
>>> ds.read_items()


"""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import re
from typing import Any, IO, Optional

import jsonlines
import yaml

from commoneval import DATAPATH
from commoneval import item


@dataclass
class Dataset:
    # by convention, the collection of Items is in a file whose name
    # is derived from the identifier. If multiple files are used, they
    # should be named in hasPart.
    identifier: str
    # when initially created
    created: date
    # who created the dataset. "Gloo" or "Biblica" are high-likelihood values
    creator: Any
    # an account of the content of the dataset
    description: str
    # one or more files that together comprise the dataset
    hasPart: list[str]
    # the source of this data
    source: str
    # perhaps these values should come from a controlled vocabulary someday
    subject: str
    # -- optional attributes
    # individuals who contributed to the dataset
    contributor: Optional[Any] = None
    # when the dataset was published (if published)
    datePublished: Optional[date] = None
    # populate with read_items()
    items: list[item.BaseItem] = field(default_factory=list)
    # ISO 639-3 code
    language: str = "eng"
    # should be a standard license identifier
    license: str = "CC-BY-NC-SA-4.0"
    # if the license isn't clear or is not a standard one, here's a
    # place to put comments
    licenseNotes: str = ""
    # which version of the metadata spec this dataset and its items conform to
    metadataVersion: str = "3.2"
    # only specify if different from creator
    publisher: Optional[Any] = None
    # how the items were generated
    sourceProcess: str = ""
    taskPrompt: str = ""
    title: str = ""
    version: str = "1.0"
    _localPath: Optional[Path] = None
    _extension: str = "jsonl"
    _slugify_regex: str = r"[^-a-zA-Z0-9_.]+"

    def __post_init__(self) -> None:
        """Check values after initialization."""
        assert re.fullmatch(
            r"[-a-zA-Z0-9_.]+", self.identifier
        ), f"Identifier {self.identifier} has invalid characters."
        # check that the created date is in the past
        assert self.created <= date.today(), "Created date must be in the past."
        # if a single file, identifier+extension; if multiple files, identifier_000.jsonl, etc.
        if len(self.hasPart) == 1:
            assert (
                self.hasPart[0] == f"{self.identifier}.{self._extension}"
            ), f"File name {self.hasPart[0]} does not match single file convention for identifier {self.identifier!r}."
        else:
            for i, part in enumerate(self.hasPart):
                assert (
                    part == f"{self.identifier}_{str(i).zfill(3)}.{self._extension}"
                ), f"File name {part} does not match multiple file convention for identifier {self.identifier!r}."
        if self.datePublished:
            # check that the date published is in the past
            assert (
                self.datePublished <= date.today()
                and self.datePublished >= self.created
            ), "Date published must be in the past and after created."
        self._localPath = DATAPATH / self.language / self.identifier

    def __repr__(self) -> str:
        """Return a string representation of the Dataset."""
        return f"<Dataset({self.identifier!r}, {self.subject!r})>"

    def __len__(self) -> int:
        """Return the number of items in the Dataset."""
        return len(self.items)

    def asdict(self) -> dict[str, Any]:
        """Return the Dataset as a dictionary for serialization."""
        return {
            "identifier": self.identifier,
            "contributor": self.contributor,
            "created": self.created.isoformat(),
            "creator": self.creator,
            "datePublished": (
                self.datePublished.isoformat() if self.datePublished else None
            ),
            "description": self.description,
            "hasPart": self.hasPart,
            "language": self.language,
            "license": self.license,
            "licenseNotes": self.licenseNotes,
            "metadataVersion": self.metadataVersion,
            "publisher": self.publisher,
            "source": self.source,
            "sourceProcess": self.sourceProcess,
            "subject": self.subject,
            "taskPrompt": self.taskPrompt,
            "title": self.title,
            "version": self.version,
        }

    @staticmethod
    def fromdict(data: dict[str, Any]) -> None:
        """Load the Dataset from a dictionary."""
        safedata = data.copy()
        for key, value in safedata.items():
            if key in ["created", "datePublished"] and value:
                newvalue = date.fromisoformat(value)
                safedata[key] = newvalue
        return Dataset(**safedata)

    @staticmethod
    def read_yaml(fp: IO[str]) -> "Dataset":
        """Read the Dataset metadata from a YAML file.

        Does not read the items.
        """
        ydict = yaml.safe_load(fp)
        return Dataset.fromdict(ydict)

    def write_yaml(self, fp: IO[str]) -> None:
        """Write the Dataset metadata to a YAML file."""
        # write to file
        fp.write(yaml.dump(self.asdict(), sort_keys=False))

    def read_items(
        self, itemclass: item.BaseItem, basepath: Optional[Path] = None
    ) -> None:
        """Read the items from the dataset files.

        Args:
            itemclass: The class to use for the items (e.g., item.ClosedSetItem).

        """
        mcq_modalities = (
            "choiceof2",
            "choiceof3",
            "choiceof4",
            "choiceof5",
        )
        if not basepath:
            basepath = self._localPath
        # this drops any existing items
        self.items = []
        for part in self.hasPart:
            with jsonlines.open(basepath / part, "r") as reader:
                for obj in reader:
                    if "otherargs" in obj and "choices" in obj["otherargs"]:
                        obj["choices"] = obj["otherargs"].get("choices", [])
                    if obj["modality"] in mcq_modalities:
                        letter = obj["response"]
                        obj["response"] = ord(letter.lower()) - ord("a")
                    # convert modality string to enum
                    obj["modality"] = item.Modality(obj["modality"])
                    self.items.append(itemclass(**obj))
            print(f"Read {len(self.items)} items from {part}")
        return None
