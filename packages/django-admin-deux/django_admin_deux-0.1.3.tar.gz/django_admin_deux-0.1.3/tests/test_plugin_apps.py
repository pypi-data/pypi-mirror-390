"""Tests for plugin-driven INSTALLED_APPS management."""

from djadmin.apps import djadmin_apps


class TestPluginDrivenApps:
    """Test djadmin_apps() function."""

    def test_djadmin_apps_includes_core(self):
        """Test that djadmin is always included."""
        apps = djadmin_apps()
        assert 'djadmin' in apps

    def test_djadmin_apps_includes_plugins(self):
        """Test that plugin apps are included."""
        apps = djadmin_apps()

        # Core plugin should be included
        assert 'djadmin.plugins.core' in apps

        # Theme plugin should be included
        assert 'djadmin.plugins.theme' in apps

    def test_djadmin_apps_respects_first(self):
        """Test that First() ordering is respected (theme loads first)."""
        apps = djadmin_apps()

        # Theme should be first
        assert apps[0] == 'djadmin.plugins.theme', f'Theme plugin should be first, but got: {apps[0]}'

        # And theme should come before djadmin
        theme_idx = apps.index('djadmin.plugins.theme')
        djadmin_idx = apps.index('djadmin')

        assert theme_idx < djadmin_idx, (
            f'Theme plugin should come before djadmin core, but got: ' f'theme at {theme_idx}, djadmin at {djadmin_idx}'
        )

    def test_djadmin_apps_removes_duplicates(self):
        """Test that duplicate apps are removed."""
        apps = djadmin_apps()

        # No duplicates
        assert len(apps) == len(set(apps)), f'Found duplicates in: {apps}'

    def test_djadmin_apps_returns_list(self):
        """Test that djadmin_apps returns a list."""
        apps = djadmin_apps()
        assert isinstance(apps, list)
        assert all(isinstance(app, str) for app in apps)

    def test_djadmin_formset_before_djadmin(self):
        """Test that djadmin_formset comes before djadmin for template override."""
        apps = djadmin_apps()

        # Both should be included
        assert 'djadmin_formset' in apps
        assert 'djadmin' in apps

        # djadmin_formset should come before djadmin
        formset_idx = apps.index('djadmin_formset')
        djadmin_idx = apps.index('djadmin')

        assert formset_idx < djadmin_idx, (
            f'djadmin_formset should come before djadmin for template overrides, '
            f'but got: djadmin_formset at {formset_idx}, djadmin at {djadmin_idx}'
        )


class TestPluginHookImplementations:
    """Test plugin hook implementations."""

    def test_core_plugin_hook(self):
        """Test core plugin returns required apps."""
        from djadmin.plugins.core.djadmin_hooks import djadmin_get_required_apps

        apps = djadmin_get_required_apps()
        assert 'djadmin.plugins.core' in apps

    def test_theme_plugin_hook(self):
        """Test theme plugin returns apps with First."""
        from djadmin.plugins.modifiers import First
        from djadmin.plugins.theme.djadmin_hooks import djadmin_get_required_apps

        apps = djadmin_get_required_apps()

        # Should contain a First() wrapper
        assert any(isinstance(app, First) for app in apps)

    def test_theme_plugin_uses_first(self):
        """Test theme plugin specifies First('djadmin.plugins.theme')."""
        from djadmin.plugins.modifiers import First
        from djadmin.plugins.theme.djadmin_hooks import djadmin_get_required_apps

        apps = djadmin_get_required_apps()

        # Find the First modifier
        first_modifiers = [app for app in apps if isinstance(app, First)]
        assert len(first_modifiers) > 0, 'Theme plugin should have at least one First() modifier'

        # Check that it's the theme app
        first = first_modifiers[0]
        assert first.app == 'djadmin.plugins.theme'
