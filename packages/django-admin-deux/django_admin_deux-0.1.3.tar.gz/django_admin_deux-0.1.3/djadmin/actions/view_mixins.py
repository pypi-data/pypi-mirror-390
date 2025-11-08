"""View type mixins for actions

These mixins define which Django CBV base class an action should use.
They are minimal - just specifying the base_class. Individual actions
add their own specific logic.
"""

from django.core.exceptions import ImproperlyConfigured
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from djadmin.views import BulkDeleteView


class FormFeaturesMixin:
    """
    Mixin for actions that use forms and need feature validation.

    Provides methods to detect required features (like collections, conditional fields)
    and validate that necessary plugins are installed.

    Used by AddAction and EditRecordAction to ensure Layout API features
    are available when needed.
    """

    def get_form_features(self):
        """
        Get features required by this form.

        Checks the ModelAdmin's layout for required features and allows
        plugins to add more via the djadmin_get_form_features hook.

        Uses action-specific layout if available:
        - CreateViewActionMixin → create_layout or layout
        - UpdateViewActionMixin → update_layout or layout

        Returns:
            Set of feature names (strings) like 'collections', 'conditional_fields', etc.
        """
        from djadmin.plugins import pm

        features = set()

        # Get action-specific layout (inline to avoid MRO issues with view instances)
        layout = None
        if isinstance(self, CreateViewActionMixin):
            # Create action: use create_layout or fallback to layout
            layout = getattr(self.model_admin, 'create_layout', None) or getattr(self.model_admin, 'layout', None)
        elif isinstance(self, UpdateViewActionMixin):
            # Update action: use update_layout or fallback to layout
            layout = getattr(self.model_admin, 'update_layout', None) or getattr(self.model_admin, 'layout', None)
        else:
            # Other actions: use generic layout
            layout = getattr(self.model_admin, 'layout', None)

        if layout:
            features.update(layout.get_features())

        # Let plugins add more features
        for plugin_features in pm.hook.djadmin_get_form_features(
            action=self,
            model_admin=self.model_admin,
        ):
            if plugin_features:
                features.update(plugin_features)

        return features

    def validate_features(self):
        """
        Validate that required features are available.

        Called during form class generation. If required features are missing,
        raises ImproperlyConfigured with helpful error messages.

        This uses the plugin feature advertising system to check if required
        features are provided by registered plugins.

        Raises:
            ImproperlyConfigured: If required features are not available
        """
        from djadmin.plugins import pm

        features = self.get_form_features()

        if not features:
            return  # No special features needed

        # Get all provided features from plugins
        all_provided_features = set()
        results = pm.hook.djadmin_provides_features()
        for feature_list in results:
            if feature_list:
                all_provided_features.update(feature_list)

        # Check if features are satisfied
        missing_features = features - all_provided_features

        if missing_features:
            # Build helpful error message
            feature_messages = {
                'collections': ('Inline editing (Collection components) requires ' 'the djadmin-formset plugin'),
                'inlines': ('Inline editing (Collection components) requires ' 'the djadmin-formset plugin'),
                'conditional_fields': ('Conditional fields (show_if/hide_if) require ' 'the djadmin-formset plugin'),
                'computed_fields': ('Computed fields (calculate) require ' 'the djadmin-formset plugin'),
            }

            messages = []
            for feature in missing_features:
                if feature in feature_messages:
                    messages.append(feature_messages[feature])
                else:
                    messages.append(f"Feature '{feature}' is not provided by any plugin")

            # De-duplicate messages
            messages = list(dict.fromkeys(messages))

            raise ImproperlyConfigured(
                f'Form for {self.model._meta.verbose_name} requires '
                f'features that are not available:\n'
                + '\n'.join(f'  • {msg}' for msg in messages)
                + '\n\nInstall with: pip install django-admin-deux[djadmin-formset]'
            )


class FormViewActionMixin:
    """
    Mixin for actions that use FormView.

    Use for actions that display and process non-model forms (plain Form, not ModelForm).
    For model forms, use CreateViewActionMixin or UpdateViewActionMixin instead.

    Example:
        class ChangeStatusAction(BulkActionMixin, FormViewActionMixin, BaseAction):
            form_class = StatusForm  # Plain Form
    """

    base_class = FormView


class CreateViewActionMixin:
    """
    Mixin for actions that use CreateView.

    Use for actions that create new model instances with a ModelForm.
    CreateView automatically generates forms and handles saving.

    Example:
        class AddAction(GeneralActionMixin, CreateViewActionMixin, BaseAction):
            pass
    """

    base_class = CreateView


class UpdateViewActionMixin:
    """
    Mixin for actions that use UpdateView.

    Use for actions that update existing model instances with a ModelForm.
    UpdateView automatically generates forms and handles saving.

    Example:
        class EditRecordAction(RecordActionMixin, UpdateViewActionMixin, BaseAction):
            pass
    """

    base_class = UpdateView


class ListViewActionMixin:
    """
    Mixin for actions that use ListView.

    Use for actions that display lists of objects with pagination.
    Typically the main list view for a model.

    Example:
        class ListViewAction(ListViewActionMixin, BaseAction):
            pass
    """

    base_class = ListView


class TemplateViewActionMixin:
    """
    Mixin for actions that use TemplateView.

    Use for actions that render simple templates without object/queryset.
    Common for confirmation pages.

    Example:
        class ConfirmDeleteAction(RecordActionMixin, TemplateViewActionMixin, BaseAction):
            pass
    """

    base_class = TemplateView


class DeleteViewActionMixin:
    """
    Mixin for actions that use DeleteView.

    Use for actions that delete model instances with confirmation.
    DeleteView automatically handles GET (show confirmation) and POST (delete).

    Example:
        class DeleteRecordAction(RecordActionMixin, DeleteViewActionMixin, BaseAction):
            pass
    """

    base_class = DeleteView


class BulkDeleteViewActionMixin:
    """
    Mixin for actions that use BulkDeleteView.

    Use for actions that delete multiple selected model instances with confirmation.
    BulkDeleteView handles GET (show confirmation) and POST (delete selected).

    Example:
        class DeleteBulkAction(BulkActionMixin, BulkDeleteViewActionMixin, BaseAction):
            pass
    """

    base_class = BulkDeleteView


class RedirectViewActionMixin:
    """
    Mixin for actions that use RedirectView.

    Use for actions that redirect to another URL.
    The action should implement get_redirect_url().

    Example:
        class ViewRecordAction(RecordActionMixin, RedirectViewActionMixin, BaseAction):
            def get_redirect_url(self, request, obj):
                return obj.get_absolute_url()
    """

    base_class = RedirectView


class DetailViewActionMixin:
    """
    Mixin for actions that use DetailView (read-only display).

    Use for actions that display model instances in read-only mode using
    the Layout API for structured display.

    The action can define a view_layout attribute on the ModelAdmin, or it will
    fall back to update_layout, layout, or auto-generate layout from model fields.

    Example:
        class ViewRecordAction(RecordActionMixin, DetailViewActionMixin, BaseAction):
            pass

        # In ModelAdmin:
        class ProductAdmin(ModelAdmin):
            view_layout = Layout(
                Fieldset('Details',
                    Field('name'),
                    Field('price'),
                ),
            )
    """

    base_class = DetailView

    def get_layout(self):
        """
        Get layout for display.

        Fallback order:
        1. view_layout (action-specific)
        2. update_layout (shares with edit view)
        3. layout (generic)
        4. Auto-generate from model fields

        Returns:
            Layout instance or None
        """
        # Try view_layout first (most specific)
        layout = getattr(self.model_admin, 'view_layout', None)
        if layout:
            return layout

        # Fallback to update_layout (share with edit view)
        layout = getattr(self.model_admin, 'update_layout', None)
        if layout:
            return layout

        # Fallback to generic layout
        layout = getattr(self.model_admin, 'layout', None)
        if layout:
            return layout

        # No layout defined - auto-generate from model fields
        return None

    def _auto_generate_layout(self):
        """
        Auto-generate layout from model fields.

        Returns:
            Layout instance with all model fields
        """
        from djadmin.layout import Field, Layout

        # Get all model fields
        fields = []
        for field in self.model._meta.get_fields():
            if not field.auto_created and hasattr(field, 'name'):
                fields.append(Field(field.name))

        if not fields:
            return None

        return Layout(*fields)

    def get_context_data(self, **kwargs):
        """
        Add layout_items to context for template rendering.

        Returns:
            Context dict with layout_items
        """
        context = super().get_context_data(**kwargs)

        # Get layout
        layout = self.get_layout()

        if layout:
            # Render layout for display
            obj = self.get_object()
            layout_items = layout.render_for_display(obj)
            context['layout_items'] = layout_items

        return context
