"""Utility functions for core plugin."""


def copy_model_admin_attrs(action, attrs):
    """
    Copy attributes from action.model_admin to view.

    Args:
        action: Action instance with model_admin attribute
        attrs: List of attribute names to copy

    Returns:
        Dict mapping attribute names to their values from model_admin
    """
    return {attr: getattr(getattr(action, 'model_admin', None), attr, None) for attr in attrs}
