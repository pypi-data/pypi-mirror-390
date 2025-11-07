from ._swordfishcpp import pyobjs_init  # type: ignore


class ModuleResources(object):
    # static
    _instanc = None
    _initial = False

    def __new__(cls, *args, **kwargs):
        if cls._instanc is None:
            cls._instanc = super().__new__(cls)
        return cls._instanc

    def __init__(self) -> None:
        if not self._initial:
            pyobjs_init()
            self._initial = True
