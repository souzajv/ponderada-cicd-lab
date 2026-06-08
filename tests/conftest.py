import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def ci_mode() -> dict:
    path = ROOT / "ci-mode.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def apply_ci_mode_flags(ci_mode: dict) -> None:
    if ci_mode.get("force_test_failure"):
        os.environ["FORCE_TEST_FAILURE"] = "1"
    else:
        os.environ.pop("FORCE_TEST_FAILURE", None)
