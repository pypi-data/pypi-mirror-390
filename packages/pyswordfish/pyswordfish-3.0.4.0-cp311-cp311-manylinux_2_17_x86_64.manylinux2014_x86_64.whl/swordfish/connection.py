from .tools import check_import_pro

from ._connection import meta_code, empty_context

if check_import_pro():
    from ._connection import connect, list_catalogs, exists_catalog, create_catalog, drop_catalog
    from ._connection import Connection, DefaultSessionConnection, OLTPConnection, CatalogConnection
    from ._connection import Schema, Partition, OLTPOption
    from ._connection import StorageType
    from ._connection import RemoteTable, RemoteConnection

__all__ = [
    "Connection",
    "DefaultSessionConnection",
    "OLTPConnection",
    "CatalogConnection",
    "Schema",
    "Partition",
    "StorageType",
    "OLTPOption",

    "connect",
    "list_catalogs",
    "exists_catalog",
    "create_catalog",
    "drop_catalog",

    "meta_code",
    "empty_context",

    "RemoteTable",
    "RemoteConnection",
]
