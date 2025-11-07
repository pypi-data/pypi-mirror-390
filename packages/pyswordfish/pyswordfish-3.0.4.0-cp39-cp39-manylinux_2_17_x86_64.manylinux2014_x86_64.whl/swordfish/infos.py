from ._swordfishcpp import (  # type: ignore
    get_home_dir,
    get_working_dir,
    get_exec_dir,
    sw_is_ce_edition,
)
from ._runtime import (
    Runtime,
)
from .tools import Edition, get_server_version


class Info:
    @property
    def HOME_DIR(self):
        return get_home_dir()

    @property
    def WORKING_DIR(self):
        return get_working_dir()

    @property
    def EXEC_DIR(self):
        return get_exec_dir()

    @property
    def EDITION(self):
        if sw_is_ce_edition():
            return Edition.CE
        return Edition.PRO

    @property
    def HOST(self):
        return Runtime()._host

    @property
    def PORT(self):
        return Runtime()._port

    @property
    def ALIAS(self):
        return Runtime()._alias

    @property
    def VERSION(self):
        return get_server_version()


info = Info()

__all__ = [
    "info",
]
