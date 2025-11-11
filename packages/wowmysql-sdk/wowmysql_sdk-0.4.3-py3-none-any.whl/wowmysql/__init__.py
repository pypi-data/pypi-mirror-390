"""
WowMySQL Python SDK
Official client library for WowMySQL REST API v2
"""

from .auth import (
    ProjectAuthClient,
    AuthResponse,
    AuthSession,
    AuthUser,
    TokenStorage,
    MemoryTokenStorage,
)
from .client import WowMySQLClient, WowMySQLError
from .table import Table, QueryBuilder
from .types import (
    QueryOptions,
    FilterExpression,
    QueryResponse,
    CreateResponse,
    UpdateResponse,
    DeleteResponse,
    TableSchema,
    ColumnInfo,
)
from .storage import (
    WowMySQLStorage,
    StorageQuota,
    StorageFile,
    StorageError,
    StorageLimitExceededError,
)

__version__ = "0.4.1"
__all__ = [
    # Database Client
    "WowMySQLClient",
    "WowMySQLError",
    "ProjectAuthClient",
    "Table",
    "QueryBuilder",
    # Types
    "QueryOptions",
    "FilterExpression",
    "QueryResponse",
    "CreateResponse",
    "UpdateResponse",
    "DeleteResponse",
    "TableSchema",
    "ColumnInfo",
    # Storage Client
    "WowMySQLStorage",
    "StorageQuota",
    "StorageFile",
    "StorageError",
    "StorageLimitExceededError",
    # Auth
    "AuthUser",
    "AuthSession",
    "AuthResponse",
    "TokenStorage",
    "MemoryTokenStorage",
]
