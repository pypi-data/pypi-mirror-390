# djadmin/plugins/permissions/__init__.py

from djadmin.plugins.permissions.permissions import (
    AllowAny,
    AnonReadOnly,
    BasePermission,
    HasDjangoPermission,
    HasDjangoPermissionOrReadOnly,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsStaff,
    IsSuperuser,
)

__all__ = [
    'AllowAny',
    'AnonReadOnly',
    'BasePermission',
    'HasDjangoPermission',
    'HasDjangoPermissionOrReadOnly',
    'IsAuthenticated',
    'IsAuthenticatedOrReadOnly',
    'IsStaff',
    'IsSuperuser',
]
