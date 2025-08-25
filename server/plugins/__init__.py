from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Callable, List


Hook = Callable[[dict], None]


class PluginManager:
    def __init__(self) -> None:
        self._event_hooks: List[Hook] = []
        self._operation_hooks: List[Hook] = []

    def register_event_hook(self, hook: Hook) -> None:
        self._event_hooks.append(hook)

    def register_operation_hook(self, hook: Hook) -> None:
        self._operation_hooks.append(hook)

    def on_event(self, event: dict) -> None:
        for h in list(self._event_hooks):
            try:
                h(event)
            except Exception:
                pass

    def on_operation(self, payload: dict) -> None:
        for h in list(self._operation_hooks):
            try:
                h(payload)
            except Exception:
                pass

    def load_plugins(self, plugins_dir: Path) -> None:
        plugins_dir.mkdir(parents=True, exist_ok=True)
        for py in plugins_dir.glob("*.py"):
            mod_name = f"emulator_plugin_{py.stem}"
            spec = importlib.util.spec_from_file_location(mod_name, py)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            try:
                spec.loader.exec_module(module)
            except Exception:
                continue
            # Optional registration functions
            if hasattr(module, "register_event_hook"):
                try:
                    self.register_event_hook(getattr(module, "register_event_hook")())
                except Exception:
                    pass
            if hasattr(module, "register_operation_hook"):
                try:
                    self.register_operation_hook(getattr(module, "register_operation_hook")())
                except Exception:
                    pass


plugin_manager = PluginManager()

