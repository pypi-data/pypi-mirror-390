"""Custom Django CBVs for djadmin

These are views that don't exist in Django's generic views but follow
the same patterns and conventions.
"""

from django import forms
from django.contrib import messages
from django.views.generic import FormView
from django.views.generic.list import MultipleObjectMixin


class BulkDeleteView(MultipleObjectMixin, FormView):
    """
    View for deleting multiple objects with confirmation.

    This view follows Django CBV patterns:
    - GET: Shows confirmation form with list of objects to delete
    - POST: Processes form and deletes selected objects

    Attributes:
        model: The model class (required, inherited from MultipleObjectMixin)
        template_name: Template for confirmation page
        success_url: URL to redirect after deletion
        context_object_name: Name for queryset in template context (default: 'object_list')
        form_class: Form class (auto-generated if not provided)
    """

    form_class = None

    def get_form_class(self):
        """
        Get form class for bulk delete.

        Auto-generates a form with ModelMultipleChoiceField if not provided.
        """
        if self.form_class:
            return self.form_class

        # Auto-generate form with ModelMultipleChoiceField
        # Use _selected_action to match ListView's checkbox name
        class BulkDeleteForm(forms.Form):
            _selected_action = forms.ModelMultipleChoiceField(
                queryset=self.model.objects.all(),
                widget=forms.MultipleHiddenInput,
                required=True,
            )

        return BulkDeleteForm

    def get_queryset(self):
        """Get queryset of objects to delete."""
        # Get PKs from request (either GET or POST)
        pks = self.request.POST.getlist('_selected_action') or self.request.GET.getlist('_selected_action')
        return self.model.objects.filter(pk__in=pks)

    def get(self, request, *args, **kwargs):
        """Handle GET request - show confirmation form."""
        # Set object_list for MultipleObjectMixin
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request - process form and delete."""
        # Set object_list for MultipleObjectMixin
        self.object_list = self.get_queryset()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Add selected objects to form kwargs."""
        kwargs = super().get_form_kwargs()

        # For GET requests, populate initial data with object_list
        if self.request.method == 'GET':
            kwargs['initial'] = {'_selected_action': self.object_list}

        return kwargs

    def get_context_data(self, **kwargs):
        """Add queryset and count to context."""
        context = super().get_context_data(**kwargs)

        # MultipleObjectMixin already adds object_list to context
        # Just add the count
        context['objects_count'] = context['object_list'].count()

        return context

    def form_valid(self, form):
        """Delete selected objects."""
        selected_objects = form.cleaned_data['_selected_action']
        count = selected_objects.count()

        # Delete the objects
        selected_objects.delete()

        # Add success message
        messages.success(
            self.request,
            f'Successfully deleted {count} {self.model._meta.verbose_name_plural}',
        )

        return super().form_valid(form)
