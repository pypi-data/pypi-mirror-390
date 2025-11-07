from ._swordfishcpp import (  # type: ignore
    check_aggregate_function,
    check_builtin_function,
    check_is_nothing,
    get_function_info,
    sw_is_ce_edition,

    check_plugin_license,

    get_server_info,
    get_server_version,
    get_plugin_info,
    get_plugin_version,
)


import socket
from typing import Tuple
from enum import Enum


class Edition(Enum):
    CE = 0
    PRO = 1


def parse_site(site: str) -> Tuple[str, int, str]:
    v = site.split(':')
    if len(v) != 3:
        raise RuntimeError(f"Invalid local site: {site}.")
    # host, port, alias
    return (v[0], int(v[1]), v[2])


def get_random_available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def check_import_pro():
    return not sw_is_ce_edition()


def assert_cannot_import_ce():
    if sw_is_ce_edition():
        raise ImportError("Please install swordfish package with a special license.")
    return True


__all__ = [
    "check_aggregate_function",
    "check_builtin_function",
    "check_is_nothing",
    "get_function_info",

    "check_plugin_license",

    "get_random_available_port",
    "parse_site",

    "check_import_pro",
    "assert_cannot_import_ce",

    "Edition",

    "get_server_info",
    "get_server_version",
    "get_plugin_info",
    "get_plugin_version",
]
