from pathlib import Path

ROOT = Path(__file__).parent.parent
DATAPATH = ROOT / "data"
# where English datasets go
DATAENGPATH = ROOT / "data/eng"
SRCPATH = ROOT / "src"

__all__ = [
    "ROOT",
    "DATAPATH",
    "DATAENGPATH",
    "SRCPATH",
]
