from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from veox.dummy import DummyDougServer


@pytest.fixture
def sample_features() -> List[List[float]]:
    return [[1.0, 2.0], [3.0, 4.0]]


@pytest.fixture
def sample_targets() -> List[int]:
    return [0, 1]


@pytest.fixture
def model_path(tmp_path: Path) -> Path:
    return tmp_path / "veox_model.json"


@pytest.fixture
def dummy_doug_server() -> DummyDougServer:
    with DummyDougServer() as server:
        yield server

