from __future__ import annotations

import threading


class Singleton(type):
    instance: type | None

    def __init__(
        cls, name: str, bases: tuple[type[object], ...], namespace: dict[str, object]
    ) -> None:
        super().__init__(name, bases, namespace)
        cls.instance = None
        cls._lock = threading.Lock()

    def __call__(cls) -> type:
        if cls.instance is None:
            with cls._lock:
                if cls.instance is None:
                    cls.instance = super().__call__()
        return cls.instance
