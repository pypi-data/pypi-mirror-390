"""Base action classes and mixins"""

from functools import cached_property

from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.utils.text import camel_case_to_spaces


class BaseAction:
    """
    Base class for all actions.

    Actions represent operations that can be performed on models.
    They can be triggered from ListView (list/bulk actions) or
    from individual records (record actions).
    """

    # Display configuration
    label: str = None  # Display name (required)
    icon: str = None  # Icon name/class (optional)
    css_class: str = ''  # Additional CSS classes

    # Behavior configuration
    confirmation_required: bool = False  # Show confirmation before execute
    http_method: str = 'GET'  # HTTP method for triggering this action ('GET' or 'POST')

    # Permission configuration
    django_permission_name: str = 'view'  # Django permission name (e.g., 'add', 'change', 'view', 'delete')
    permission_class = None  # Permission callable (overrides ModelAdmin global permission)

    def __init__(self, model, model_admin, admin_site, permission_class=None):
        """
        Initialize action with model and admin context.

        Args:
            model: The Django model class (optional, can be None for site-level actions)
            model_admin: The ModelAdmin instance (optional, can be None for site-level actions)
            admin_site: The AdminSite instance
            permission_class: Permission callable (overrides ModelAdmin global permission)
        """
        self.model = model
        self.model_admin = model_admin
        self.admin_site = admin_site

        # Override permission_class if provided
        if permission_class is not None:
            self.permission_class = permission_class

        if self.label is None:
            raise ValueError(f'{self.__class__.__name__} must define label')

    @property
    def action_name(self):
        return camel_case_to_spaces(self.__class__.__name__).replace(' ', '_').replace('_action', '')

    @property
    def url_name(self) -> str:
        """
        Get URL name for this action.

        Can be overridden by setting _url_name class attribute.

        Returns:
            URL name string
        """
        # Check if class has explicit _url_name set
        if hasattr(self.__class__, '_url_name'):
            opts = self.model._meta
            return f'{opts.app_label}_{opts.model_name}_{self.__class__._url_name}'

        # Otherwise generate from class name
        opts = self.model._meta
        return f'{opts.app_label}_{opts.model_name}_{self.action_name}'

    def get_url_pattern(self) -> str:
        """
        Get URL pattern for this action.

        Override this to customize the URL pattern for the action.
        Default pattern is: {app_label}/{model_name}/{action__name}/

        Returns:
            URL pattern string (without leading slash)
        """
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/{self.action_name}/'

    def get_url_name(self) -> str:
        """
        Get URL name for this action (deprecated, use url_name property).

        Returns:
            URL name string
        """
        return self.url_name

    def get_base_class(self):
        """
        Get view base class for this action.

        Looks through MRO for view-type mixins that define base_class.
        This allows actions to specify their view type through mixins.

        Example:
            class MyAction(FormViewActionMixin, BaseAction):
                pass

            action.get_base_class()  # Returns FormView

        Returns:
            View class from mixin or TemplateView as fallback
        """
        for base in self.__class__.__mro__:
            if hasattr(base, 'base_class'):
                return base.base_class

        # Default fallback
        from django.views.generic import TemplateView

        return TemplateView

    def get_template_names(self):
        """
        Get template names as a list (Django CBV expects plural method).

        This wraps get_template_name() and ensures the result is a list.

        Returns:
            List of template path strings
        """
        template_names = []

        if model_name := getattr(getattr(self.model, '_meta', None), 'model_name', None):
            template_names.append(f'djadmin/{self.model._meta.app_label}/{model_name}_{self.action.action_name}.html')
        template_names.append(f'djadmin/actions/{self.action.action_name}.html')

        return template_names

    @cached_property
    def view_class(self):
        """
        Cached view class for this action.

        The view class is created once via ViewFactory and cached for the
        lifetime of the action instance. This eliminates the overhead of
        recreating view classes on every permission check.

        Performance Impact:
            Without caching: 10+ view class creations per ListView request
            With caching: 1 view class creation per action (first permission check)

        Returns:
            View class ready for .as_view()
        """
        from djadmin.factories import ViewFactory

        factory = ViewFactory()
        return factory.create_view(action=self)

    def get_view_class(self):
        """
        Get the view class for this action via ViewFactory.

        This method delegates to the cached view_class property to avoid
        recreating view classes on every call. Provided for backward
        compatibility and API consistency.

        Returns:
            View class ready for .as_view()
        """
        return self.view_class

    def check_permission(self, request: HttpRequest, obj=None) -> bool:
        """
        Check if user has permission to execute this action.

        This method creates a minimal view instance with the request and action
        context, then calls the test_func() permission check. This allows actions
        to be filtered in templates and list views without actually executing them.

        Args:
            request: The HTTP request with user information
            obj: Optional specific object instance for object-level permissions

        Returns:
            bool: True if user has permission, False otherwise
        """
        # Get the cached view class
        view_class = self.view_class

        # Create a minimal view instance with request context
        view = view_class()
        view.request = request
        view.action = self
        view.model = self.model
        view.model_admin = self.model_admin
        view.admin_site = self.admin_site

        # Set object if provided (for object-level permissions)
        if obj is not None:
            view.object = obj

        # Call test_func to check permission
        # test_func is provided by PermissionMixin
        if hasattr(view, 'test_func'):
            return view.test_func()

        # If no test_func, default to allow
        return True


class GeneralActionMixin:
    """
    Mixin for actions that operate on the list view.

    List actions don't require any record selection.
    They're displayed as buttons in the ListView toolbar.

    Examples:
        - AddAction (create new record)
        - ImportAction (import multiple records)
        - ExportAllAction (export all records)
    """

    action_type = 'general'


class BulkActionMixin:
    """
    Mixin for actions that operate on multiple selected records.

    Bulk actions require checkbox selection in ListView.
    Selected record PKs are passed to the action.

    Examples:
        - DeleteBulkAction (delete selected records)
        - BulkUpdateAction (update selected records)
        - ExportSelectedAction (export selected records)
    """

    action_type = 'bulk'


class RecordActionMixin:
    """
    Mixin for actions that operate on a single record.

    Record actions are displayed in ListView rows or on detail pages.
    The target record is passed to the action.

    Examples:
        - EditRecordAction (edit record)
        - DeleteRecordAction (delete record)
        - DuplicateAction (clone record)
        - ViewRecordAction (view record details)
    """

    action_type = 'record'

    def get_url_pattern(self) -> str:
        """
        Get URL pattern for this action.

        Override this to customize the URL pattern for the action.
        Default pattern is: {app_label}/{model_name}/<int:pk>/{action_class_name}/

        Returns:
            URL pattern string (without leading slash)
        """
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/<int:pk>/{self.action_name}/'


class FormActionMixin:
    """
    Mixin for actions that display an embedded custom form (Pattern A).

    This is for actions that show a simple form (typically in a modal/dialog)
    where the action itself handles form processing. The form is usually a
    plain django.forms.Form (not ModelForm) and submission is handled by
    the action's execute() method.

    Use this for: ChangeStatusAction, SendEmailAction, BulkUpdateAction
    NOT for: AddAction, EditRecordAction (use ViewActionMixin instead)

    Attributes:
        form_class: Form class to use (required for this mixin)
        template_name: Template to use (optional, uses default if None)
    """

    form_class: type[Form] | None = None
    template_name: str | None = None

    def get_form_class(self) -> type[Form]:
        """
        Get form class for this action.

        Returns:
            Form class
        """
        if self.form_class is None:
            raise ValueError(f'{self.__class__.__name__} must define form_class when using FormActionMixin')
        return self.form_class

    def get_form(self, request: HttpRequest, **kwargs) -> Form:
        """
        Instantiate form for display or processing.

        Args:
            request: The HTTP request
            **kwargs: Additional form kwargs

        Returns:
            Form instance
        """
        form_class = self.get_form_class()

        if request.method == 'POST':
            return form_class(request.POST, request.FILES, **kwargs)
        return form_class(**kwargs)

    def get_template_name(self) -> str:
        """
        Get template name for form view.

        Returns:
            Template path string
        """
        if self.template_name:
            return self.template_name
        return 'djadmin/actions/form_modal.html'

    def form_valid(self, request: HttpRequest, form: Form, **kwargs) -> HttpResponse:
        """
        Handle valid form submission.

        Override this method to implement the action logic.

        Args:
            request: The HTTP request
            form: The valid form instance
            **kwargs: Additional context (obj, queryset, etc.)

        Returns:
            HttpResponse (typically a redirect)
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement form_valid()')

    def form_invalid(self, request: HttpRequest, form: Form, **kwargs) -> HttpResponse:
        """
        Handle invalid form submission.

        Default behavior: re-render form with errors.

        Args:
            request: The HTTP request
            form: The invalid form instance
            **kwargs: Additional context

        Returns:
            HttpResponse with form errors
        """
        from django.shortcuts import render

        context = {
            'form': form,
            'action': self,
            'opts': self.model._meta,
            **kwargs,
        }
        return render(request, self.get_template_name(), context)


class ViewActionMixin:
    """
    Mixin for actions that generate a full Django CBV (Pattern B).

    This is for actions that redirect to a complete view (CreateView, UpdateView,
    FormView, DetailView, etc.) where the view is factory-generated with all logic.
    The action provides configuration for ViewFactory or a custom view class.

    Use this for: AddAction (→ CreateView), EditRecordAction (→ UpdateView)
    NOT for: ChangeStatusAction, SendEmailAction (use FormActionMixin instead)

    Note: This is future functionality for Milestone 3. The action itself would
    be passed to ViewFactory which would generate the appropriate view based on
    the action's view-type mixin (e.g., FormViewActionMixin, DetailViewActionMixin).

    Attributes:
        view_class: Optional custom view class (bypasses factory if provided)
        view_factory: Factory class to use (default: ViewFactory)
        form_class: Form class to use (optional)
        fields: Fields to include in form (optional)
    """

    view_class: type | None = None  # Custom view class (bypasses factory)
    view_factory: type | None = None  # Factory to use (default: ViewFactory)
    form_class: type[Form] | None = None  # Form class
    fields: list = None  # Fields for form

    def get_view_class(self) -> type:
        """
        Get the view class for this action.

        If view_class is set, returns it directly (bypassing factory).
        Otherwise, uses ViewFactory to generate a view class based on the
        action's view-type mixin.

        Returns:
            View class ready for .as_view()
        """
        # If custom view_class provided, use it directly
        if self.view_class is not None:
            return self.view_class

        # Otherwise, use factory to generate view
        from djadmin.factories import ViewFactory

        factory = self.view_factory or ViewFactory()
        return factory.create_view(action=self)

    def get_view_config(self) -> dict:
        """
        Get configuration dict for this action's view.

        This provides action-specific configuration that can be used
        by the factory or custom view classes.

        Returns:
            Dict of configuration
        """
        config = {
            'model': self.model,
            'model_admin': self.model_admin,
            'admin_site': self.admin_site,
            'action': self,
        }

        # Add form configuration if applicable
        if self.form_class is not None:
            config['form_class'] = self.form_class
        if self.fields is not None:
            config['fields'] = self.fields

        return config


class ConfirmationActionMixin:
    """
    Mixin for actions that require confirmation.

    Displays a confirmation page before executing the action.
    Common for Delete actions.

    Attributes:
        confirmation_message: Message to display (optional)
        template_name: Template to use (optional)
    """

    view_type = 'confirmation'
    confirmation_message: str | None = None
    template_name: str = 'djadmin/actions/confirm.html'

    def get_confirmation_message(self, obj=None, queryset=None) -> str:
        """
        Get confirmation message to display.

        Args:
            obj: Single object (for record actions)
            queryset: Multiple objects (for bulk actions)

        Returns:
            Confirmation message string
        """
        if self.confirmation_message:
            return self.confirmation_message

        if obj:
            return f"Are you sure you want to {self.label.lower()} '{obj}'?"
        elif queryset:
            count = queryset.count()
            return f'Are you sure you want to {self.label.lower()} {count} items?'

        return f'Are you sure you want to {self.label.lower()}?'

    def get_template_name(self) -> str:
        """Get template name for confirmation view"""
        return self.template_name


class RedirectActionMixin:
    """
    Mixin for actions that redirect to a URL.

    When combined with RedirectViewActionMixin, creates a Django RedirectView
    that redirects immediately without displaying content. The redirect URL
    is determined via the RedirectViewMixin using method dispatch.

    The ViewFactory automatically:
    1. Sets RedirectView as the base class (via RedirectViewActionMixin)
    2. Adds RedirectViewMixin which implements get_redirect_url() dispatch
    3. Creates a view that redirects based on action configuration

    Redirect URL can be specified via:
    - redirect_url = 'some/url'  (simple static URL)
    - def get_redirect_url(self, *args, **kwargs)  (dynamic method)

    Examples:
        # Static redirect URL
        class StaticRedirectAction(GeneralActionMixin, RedirectViewActionMixin, BaseAction):
            label = 'Go to Dashboard'
            redirect_url = '/dashboard/'

        # Dynamic redirect URL using method
        class ExternalLinkAction(RecordActionMixin, RedirectViewActionMixin, BaseAction):
            label = 'View External'

            def get_redirect_url(self, *args, **kwargs):
                # self is the VIEW instance, not the action
                pk = self.kwargs.get('pk')
                return f'https://example.com/items/{pk}'

    Note: When implementing get_redirect_url(), remember that it will be called
    with the view as self (not the action). Access view attributes like
    self.request, self.kwargs, self.action, etc.
    """

    redirect_url: str | None = None  # Optional static redirect URL

    def get_redirect_url(self, *args, **kwargs) -> str:
        """
        Get URL to redirect to (will be called via RedirectViewMixin dispatch).

        This method is called by RedirectViewMixin with the view instance as self.

        The view instance (self) has:
        - self.action: The action instance
        - self.request: The current request
        - self.kwargs: URL kwargs (e.g., {'pk': 1})
        - self.args: URL args
        - self.model: The model class
        - self.model_admin: The ModelAdmin instance
        - self.admin_site: The AdminSite instance

        Args:
            *args: URL args from Django's RedirectView
            **kwargs: URL kwargs from Django's RedirectView

        Returns:
            URL string (absolute or relative)

        Raises:
            NotImplementedError: If not overridden and no redirect_url attribute set
        """
        raise NotImplementedError(
            f'{self.__class__.__name__} must implement get_redirect_url() ' f'or set redirect_url attribute'
        )


class DownloadActionMixin:
    """
    Mixin for actions that return file downloads.

    No view is displayed, returns HttpResponse with file attachment.

    Examples:
        - ExportCSVAction
        - ExportPDFAction
        - GenerateReportAction
    """

    def get_download_response(
        self,
        request: HttpRequest,
        obj=None,
        queryset=None,
        **kwargs,
    ) -> HttpResponse:
        """
        Generate file download response.

        Override this method to generate the file.

        Args:
            request: The HTTP request
            obj: Single object (for record actions)
            queryset: Multiple objects (for bulk/list actions)
            **kwargs: Additional context

        Returns:
            HttpResponse with Content-Disposition header
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement get_download_response()')


class WithSuccessUrlActionMixin(BaseAction):
    def get_success_url(self):
        """
        Redirect to list view after creation.

        When bound to the view, self is the view instance which has:
        - self.object: The created object
        - self.request: The current request
        """
        opts = self.model._meta
        return self.admin_site.reverse(f'{opts.app_label}_{opts.model_name}_list')
