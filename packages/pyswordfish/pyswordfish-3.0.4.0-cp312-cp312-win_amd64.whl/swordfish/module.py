from ._swordfishcpp import (  # type: ignore
    _global_exec,
    _global_call,
    FunctionDef,
    DatabaseError,
)

from ._config import config as sf_config

from typing import (
    Union,
    List,
)

from pathlib import Path


def __getattr__(name: str):
    if len(_global_call("defs", f"{name}::%")) != 0:
        return Module(name)
    raise DatabaseError(f"Can not find module {name}.")


def load_module(name: str, path: Path = None, *, reload: bool = True):
    if path is None:
        path = sf_config.moduleDir
    path = Path(path)
    namespaces = name.split("::")
    for namespace in namespaces[:-1]:
        path = path / namespace
    file_path = path / f"{namespaces[-1]}.dos"
    with open(file_path, "r") as f:
        script = f.read()
    _global_call("loadModuleFromScript", name, script, reload)
    return Module(name)


def load_module_from_script(name: Union[str, List[str]], script: Union[str, List[str]], *, reload: bool = True):
    _global_call("loadModuleFromScript", name, script, reload)
    return Module(name)


class Module:
    def __init__(self, name: str):
        self.name = name

    def __getattr__(self, name: str) -> Union["Module", FunctionDef]:
        if len(_global_call("defs", f"{self.name}::{name}")) == 0:
            if len(_global_call("defs", f"{self.name}::{name}::%")) != 0:
                return Module(f"{self.name}::{name}")
            else:
                raise AttributeError(f"Module: {self.name} has no attribute '{name}'")
        else:
            return _global_exec(f"{self.name}::{name}")

    def __str__(self):
        return f"Module({self.name})"
