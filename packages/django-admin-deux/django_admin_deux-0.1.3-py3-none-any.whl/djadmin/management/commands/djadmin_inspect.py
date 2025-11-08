"""Management command for introspecting djadmin configurations"""

import json

from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string


class Command(BaseCommand):
    """Inspect registered ModelAdmin configurations"""

    help = 'Inspect registered ModelAdmin configurations, their actions, views, forms, and inheritance hierarchies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin',
            type=str,
            help='Specific ModelAdmin class (e.g., myapp.MyModelAdmin)',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Specific model (e.g., myapp.MyModel)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['table', 'json', 'tree'],
            default='table',
            help='Output format (default: table)',
        )
        parser.add_argument(
            '--actions',
            type=str,
            choices=['general', 'list', 'bulk', 'record', 'all'],
            default='all',
            help='Filter by action type (default: all)',
        )
        parser.add_argument(
            '--site',
            type=str,
            default='djadmin.site',
            help='AdminSite instance to inspect (dotted path, default: djadmin.site)',
        )

    def handle(self, *args, **options):
        # Get AdminSite instance
        try:
            site = self._get_site(options['site'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to load site '{options['site']}': {e}"))
            return

        # Get ModelAdmin instances to inspect
        admins = self._get_admins(site, options)

        if not admins:
            self.stdout.write(self.style.WARNING('No admins found'))
            return

        # Collect introspection data
        data = [self._inspect_admin(admin) for admin in admins]

        # Format and output
        formatter = self._get_formatter(options['format'])
        output = formatter(data, options)
        self.stdout.write(output)

    def _get_site(self, site_path):
        """Import and return AdminSite instance"""
        return import_string(site_path)

    def _get_admins(self, site, options):
        """Get list of ModelAdmin instances to inspect"""
        if options['admin']:
            # Specific admin class
            try:
                return [self._get_admin_by_class(site, options['admin'])]
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to find admin '{options['admin']}': {e}"))
                return []
        elif options['model']:
            # All admins for a specific model
            try:
                return self._get_admins_by_model(site, options['model'])
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to find model '{options['model']}': {e}"))
                return []
        else:
            # All admins
            return self._get_all_admins(site)

    def _get_all_admins(self, site):
        """Get all registered ModelAdmin instances"""
        admins = []
        for _model, admin_list in site._registry.items():
            admins.extend(admin_list)
        return admins

    def _get_admins_by_model(self, site, model_path):
        """Get all admins for a specific model"""
        # Parse model_path (e.g., 'myapp.MyModel')
        app_label, model_name = model_path.rsplit('.', 1)
        model = apps.get_model(app_label, model_name)
        return site._registry.get(model, [])

    def _get_admin_by_class(self, site, class_path):
        """Get specific ModelAdmin instance by class path"""
        # Import the admin class
        admin_class = import_string(class_path)

        # Find instance in registry
        for _model, admin_list in site._registry.items():
            for admin in admin_list:
                if admin.__class__ == admin_class:
                    return admin

        raise ValueError(f'Admin class {class_path} not found in registry')

    def _inspect_admin(self, admin):
        """Collect all introspection data for a ModelAdmin"""
        return {
            'admin_class': admin.__class__.__name__,
            'admin_module': admin.__class__.__module__,
            'model': admin.model._meta.label,
            'model_name': admin.model._meta.model_name,
            'app_label': admin.model._meta.app_label,
            'actions': self._inspect_actions(admin),
            'features': self._inspect_features(admin),
            'templates': self._inspect_templates(admin),
        }

    def _inspect_actions(self, admin):
        """Inspect all actions for a ModelAdmin"""
        actions = {
            'general': [],
            'bulk': [],
            'record': [],
        }

        # Inspect general actions
        if admin.general_actions:
            for action in admin.general_actions:
                actions['general'].append(self._inspect_action(action, admin))

        # Inspect bulk actions
        if admin.bulk_actions:
            for action in admin.bulk_actions:
                actions['bulk'].append(self._inspect_action(action, admin))

        # Inspect record actions
        if admin.record_actions:
            for action in admin.record_actions:
                actions['record'].append(self._inspect_action(action, admin))

        return actions

    def _inspect_action(self, action, admin):
        """Inspect a single action"""
        # Get view class (generate it if needed)
        try:
            from djadmin.factories import ViewFactory

            factory = ViewFactory()
            view_class = factory.create_view(action)
            view_instance = view_class()
        except Exception as e:
            view_class = None
            view_error = str(e)
            view_instance = None
        else:
            view_error = None

        data = {
            'action_class': action.__class__.__name__,
            'action_module': action.__class__.__module__,
            'label': action.label,
            'url_name': action.url_name,
            'view_class': view_class.__name__ if view_class else None,
            'view_error': view_error,
            'form_class': getattr(view_instance, 'get_form_class', lambda: None)(),
            'layout': getattr(view_instance, 'get_layout', lambda: None)(),
        }

        # Get base class and mixins for view
        if view_class:
            base_class, mixins = self._get_base_and_mixins(view_class, action)
            data['view_base_class'] = base_class
            data['view_mixins'] = mixins

        # For form actions, include form info
        if form_class := data.get('form_class', None):
            try:
                if form_class:
                    data['form_class'] = form_class.__name__
                    data['form_module'] = form_class.__module__
                    data['form_mro'] = self._get_mro(form_class)
            except Exception:
                data['form_class'] = None
        else:
            data['form_class'] = None

        # For layout actions, include layout info
        if layout := data.get('layout', None):
            try:
                if layout:
                    data['layout'] = self._inspect_layout(layout)
            except Exception:
                data['layout'] = None
        else:
            data['layout'] = None

        return data

    def _get_base_and_mixins(self, view_class, action):
        """
        Get base class and mixins for a view.

        The ViewFactory creates views with: (mixin1, mixin2, ..., base_class)
        So we extract the base class (last in __bases__) and mixins (all others).
        """
        if not view_class or not hasattr(view_class, '__bases__'):
            return None, []

        bases = view_class.__bases__
        if not bases:
            return None, []

        # Last base is the base class, others are mixins
        base_class = bases[-1]
        mixins = bases[:-1] if len(bases) > 1 else []

        # Format base class info
        base_info = {
            'name': base_class.__name__,
            'module': base_class.__module__,
            'is_django': base_class.__module__.startswith('django.'),
            'is_djadmin': base_class.__module__.startswith('djadmin'),
        }

        # Format mixins info
        mixins_info = [
            {
                'name': mixin.__name__,
                'module': mixin.__module__,
                'is_django': mixin.__module__.startswith('django.'),
                'is_djadmin': mixin.__module__.startswith('djadmin'),
            }
            for mixin in mixins
        ]

        return base_info, mixins_info

    def _get_mro(self, cls):
        """Get Method Resolution Order for a class (for forms)"""
        if not cls:
            return []

        return [
            {
                'name': c.__name__,
                'module': c.__module__,
                'is_django': c.__module__.startswith('django.'),
                'is_djadmin': c.__module__.startswith('djadmin'),
            }
            for c in cls.__mro__
            if c is not object
        ]

    def _inspect_layout(self, layout):
        """Inspect a Layout object"""
        from djadmin.layout import Collection, Field, Fieldset, Row

        components = []
        for item in layout.items:
            if isinstance(item, Fieldset):
                legend = f"'{item.legend}'" if item.legend else 'None'
                components.append(f'Fieldset({legend}, {len(item.fields)} fields)')
            elif isinstance(item, Row):
                components.append(f'Row({len(item.fields)} fields)')
            elif isinstance(item, Collection):
                components.append(f"Collection('{item.name}', model={item.model.__name__})")
            elif isinstance(item, Field):
                components.append(f"Field('{item.name}')")

        return f'<Layout: {len(components)} components> - ' + ', '.join(components)

    def _inspect_features(self, admin):
        """Inspect requested and provided features"""
        from djadmin.plugins import pm

        # Requested features
        requested = admin.requested_features

        # Get all features provided by all plugins
        # Use pluggy's hook implementation tracking
        feature_providers = {}  # feature -> list of plugin names

        # Get hook implementations to identify which plugin provides which feature
        for hookimpl in pm.hook.djadmin_provides_features.get_hookimpls():
            try:
                # Call the hook implementation
                features = hookimpl.function()
                if features:
                    # Get the plugin module name (hookimpl.plugin is the module itself)
                    plugin_module_name = hookimpl.plugin.__name__

                    # Extract user-friendly plugin name
                    if plugin_module_name.startswith('djadmin.plugins.'):
                        # Built-in plugin: djadmin.plugins.core.djadmin_hooks -> djadmin-core
                        plugin_name = plugin_module_name.split('.')[2]
                        plugin_display = f'djadmin-{plugin_name}'
                    elif plugin_module_name.startswith('djadmin_'):
                        # External plugin: djadmin_formset.djadmin_hooks -> djadmin-formset
                        plugin_display = plugin_module_name.split('.')[0].replace('_', '-')
                    else:
                        # Other: use first part of module
                        plugin_display = plugin_module_name.split('.')[0]

                    # Track which plugin provides which features
                    for feature in features:
                        if feature not in feature_providers:
                            feature_providers[feature] = []
                        if plugin_display not in feature_providers[feature]:
                            feature_providers[feature].append(plugin_display)
            except Exception:
                # Skip if hook implementation fails
                pass

        # Check which requested features are provided
        provided_by = {}
        for feature in requested:
            if feature in feature_providers:
                providers = feature_providers[feature]
                provided_by[feature] = ', '.join(providers)
            else:
                provided_by[feature] = 'NOT PROVIDED'

        return {
            'requested': list(requested),
            'provided_by': provided_by,
        }

    def _inspect_templates(self, admin):
        """Get template resolution order for admin"""
        model_name = admin.model._meta.model_name
        app_label = admin.model._meta.app_label

        return [
            f'djadmin/{app_label}/{model_name}_list.html',
            f'djadmin/{app_label}/{model_name}_create.html',
            f'djadmin/{app_label}/{model_name}_update.html',
            'djadmin/model_list.html',
            'djadmin/model_create.html',
            'djadmin/model_update.html',
        ]

    def _get_formatter(self, format_type):
        """Get formatter function for output format"""
        formatters = {
            'table': self._format_table,
            'json': self._format_json,
            'tree': self._format_tree,
        }
        return formatters[format_type]

    def _format_table(self, data, options):
        """Format output as table (human-readable)"""
        output = []

        for admin_data in data:
            output.append(self._format_admin_table(admin_data, options))

        return '\n\n'.join(output)

    def _get_origin_label(self, cls_info):
        """Get origin label for a class (plugin, core, Django, etc)"""
        if cls_info['is_django']:
            return f"(Django: {cls_info['module']})"
        elif cls_info['is_djadmin']:
            if cls_info['module'].startswith('djadmin.plugins.core'):
                return '(djadmin core)'
            else:
                # Extract plugin name from module path
                # e.g., "djadmin_formset.mixins" -> "djadmin-formset"
                # or "djadmin.plugins.theme" -> "djadmin-theme"
                module = cls_info['module']
                if module.startswith('djadmin.plugins.'):
                    # Built-in plugin: djadmin.plugins.theme -> djadmin-theme
                    plugin_name = module.split('.')[2]
                    return f'(djadmin-{plugin_name})'
                else:
                    # External plugin: djadmin_formset.mixins -> djadmin-formset
                    plugin_name = module.split('.')[0]
                    return f'({plugin_name})'
        else:
            # External library - show module path
            return f"({cls_info['module']})"

    def _format_admin_table(self, admin_data, options):
        """Format a single admin as table"""
        lines = []

        # Header
        lines.append(f"ModelAdmin: {admin_data['admin_module']}.{admin_data['admin_class']} ({admin_data['model']})")
        lines.append('=' * 80)
        lines.append('')

        # Actions
        actions_filter = options.get('actions', 'all')
        if actions_filter == 'all' or actions_filter in admin_data['actions']:
            lines.append('ACTIONS:')

            action_types = ['general', 'bulk', 'record'] if actions_filter == 'all' else [actions_filter]

            for action_type in action_types:
                action_list = admin_data['actions'].get(action_type, [])
                if action_list:
                    lines.append(f'  {action_type.title()} Actions:')
                    for action in action_list:
                        view_info = (
                            action['view_class']
                            if action['view_class']
                            else f"ERROR: {action.get('view_error', 'unknown')}"
                        )
                        lines.append(f"    - {action['action_class']} → {view_info}")
                        if form_class := action.get('form_class', None):
                            lines.append(f'      Form: {form_class}')
                        if layout := action.get('layout', None):
                            lines.append(f'      Layout: {layout}')

            lines.append('')

        # View composition (for all actions)
        # Only show if action type matches the filter or filter is 'all'
        actions_filter = options.get('actions', 'all')
        action_types_to_check = ['general', 'bulk', 'record'] if actions_filter == 'all' else [actions_filter]

        for action_type in action_types_to_check:
            action_list = admin_data['actions'].get(action_type, [])
            if action_list:
                # Show all actions, not just the first one
                for action_data in action_list:
                    if action_data.get('view_base_class'):
                        lines.append(f"VIEW COMPOSITION - {action_data['action_class']}:")
                        lines.append(f"  View Class: {action_data['view_class']}")

                        # Show base class
                        base_cls = action_data['view_base_class']
                        base_origin = self._get_origin_label(base_cls)
                        lines.append(f"  Base Class: {base_cls['name']} {base_origin}")

                        # Show mixins
                        mixins = action_data.get('view_mixins', [])
                        if mixins:
                            lines.append('  Mixins:')
                            for mixin in mixins:
                                mixin_origin = self._get_origin_label(mixin)
                                lines.append(f"    - {mixin['name']} {mixin_origin}")

                        lines.append('')

        # Features
        if admin_data['features']['requested']:
            lines.append('REQUESTED FEATURES:')
            for feature in admin_data['features']['requested']:
                provider = admin_data['features']['provided_by'].get(feature, 'NOT PROVIDED')
                lines.append(f'  - {feature} (provided by: {provider})')
            lines.append('')

        # Templates
        if admin_data['templates']:
            lines.append('TEMPLATES (resolution order):')
            for template in admin_data['templates']:
                lines.append(f'  - {template}')
            lines.append('')

        return '\n'.join(lines)

    def _format_json(self, data, options):
        """Format output as JSON (machine-readable)"""
        return json.dumps(data, indent=2)

    def _format_tree(self, data, options):
        """Format output as tree (hierarchical)"""
        # For now, use table format with tree-like structure
        # Can be enhanced later with Unicode box-drawing characters
        return self._format_table(data, options)
