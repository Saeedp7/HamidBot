from __future__ import annotations

import importlib
from typing import Type

from .base import BaseStrategy


def load_strategy(name: str) -> Type[BaseStrategy]:
    module = importlib.import_module(f"strategies.{name}")
    class_members = [getattr(module, attr) for attr in dir(module)]
    for obj in class_members:
        if isinstance(obj, type) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
            return obj  # first strategy class in module
    raise ImportError(f"No strategy class found in strategies.{name}")
