"""Action system for django-admin-deux"""

from .base import (
    BaseAction,
    BulkActionMixin,
    ConfirmationActionMixin,
    DownloadActionMixin,
    FormActionMixin,
    GeneralActionMixin,
    RecordActionMixin,
    RedirectActionMixin,
    ViewActionMixin,
)
from .view_mixins import (
    CreateViewActionMixin,
    FormFeaturesMixin,
    FormViewActionMixin,
    ListViewActionMixin,
    RedirectViewActionMixin,
    TemplateViewActionMixin,
    UpdateViewActionMixin,
)

__all__ = [
    # Base classes and action type mixins
    'BaseAction',
    'GeneralActionMixin',
    'BulkActionMixin',
    'RecordActionMixin',
    'FormActionMixin',
    'ViewActionMixin',
    'ConfirmationActionMixin',
    'RedirectActionMixin',
    'DownloadActionMixin',
    # View type mixins
    'FormFeaturesMixin',
    'FormViewActionMixin',
    'CreateViewActionMixin',
    'UpdateViewActionMixin',
    'ListViewActionMixin',
    'TemplateViewActionMixin',
    'RedirectViewActionMixin',
]
