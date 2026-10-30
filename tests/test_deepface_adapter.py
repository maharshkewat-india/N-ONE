import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import deepface_adapter
from deepface_adapter import load_deepface_backend


def test_load_deepface_backend_accepts_module_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def api_function(*args: object, **kwargs: object) -> list[object]:
        return [*args, *kwargs.values()]

    backend_module = SimpleNamespace(
        represent=api_function,
        find=api_function,
        verify=api_function,
    )
    monkeypatch.setattr(deepface_adapter, "_BACKEND", None)

    def import_module(name: str) -> SimpleNamespace:
        assert name == "deepface.DeepFace"
        return backend_module

    monkeypatch.setattr(
        deepface_adapter,
        "importlib",
        SimpleNamespace(import_module=import_module),
    )

    assert load_deepface_backend() is backend_module


def test_load_deepface_backend_provides_represent_and_find() -> None:
    backend = load_deepface_backend()

    assert hasattr(backend, "represent")
    assert hasattr(backend, "find")

    results = backend.represent(img_path=np.zeros((120, 120, 3), dtype=np.uint8), enforce_detection=False)
    assert isinstance(results, list)
