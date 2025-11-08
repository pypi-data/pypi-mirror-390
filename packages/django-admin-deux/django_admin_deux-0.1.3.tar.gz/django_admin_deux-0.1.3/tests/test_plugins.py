from djadmin.plugins import pm


def test_core_plugin_loaded():
    """Core plugin should always be loaded"""
    features = set()
    for feature_list in pm.hook.djadmin_provides_features():
        features.update(feature_list or [])

    assert 'crud' in features


def test_theme_plugin_loaded():
    """Theme plugin should be auto-loaded"""
    features = set()
    for feature_list in pm.hook.djadmin_provides_features():
        features.update(feature_list or [])

    assert 'theme' in features


def test_plugin_hooks_available():
    """All expected hooks should be registered"""
    hook_names = [
        'djadmin_provides_features',
        # Action view hooks (registry-based pattern)
        'djadmin_get_action_view_mixins',
        'djadmin_get_action_view_base_class',
        'djadmin_get_action_view_assets',
        'djadmin_get_action_view_attributes',
        # Action registration and execution hooks
        'djadmin_register_actions',
        # Default action hooks
        'djadmin_get_default_general_actions',
        'djadmin_get_default_bulk_actions',
        'djadmin_get_default_record_actions',
        # Query and context hooks
        'djadmin_modify_queryset',
        'djadmin_add_context_data',
    ]

    for hook_name in hook_names:
        assert hasattr(pm.hook, hook_name)
