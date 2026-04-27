"""Make tests/_ctlrender_helper.py importable from the benchmarks package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))
