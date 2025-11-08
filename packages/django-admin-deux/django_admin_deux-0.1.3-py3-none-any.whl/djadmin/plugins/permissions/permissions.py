# djadmin/plugins/permissions/permissions.py


class PermissionMeta(type):
    """Metaclass to support operators on permission classes (not just instances)."""

    def __and__(cls, other):
        """AND composition for classes."""
        from djadmin.plugins.permissions.operators import And

        return And(cls, other)

    def __or__(cls, other):
        """OR composition for classes."""
        from djadmin.plugins.permissions.operators import Or

        return Or(cls, other)

    def __xor__(cls, other):
        """XOR composition for classes."""
        from djadmin.plugins.permissions.operators import Xor

        return Xor(cls, other)

    def __invert__(cls):
        """NOT composition for classes."""
        from djadmin.plugins.permissions.operators import Not

        return Not(cls)


class BasePermission(metaclass=PermissionMeta):
    """
    Base class for permission callables.

    Usage:
        class IsStaff(BasePermission):
            def __call__(self, view):
                return view.request.user.is_staff

        # Composition with operators (instances)
        permission_class = IsAuthenticated() & IsStaff()

        # Composition with operators (classes - auto-normalized)
        permission_class = IsAuthenticated & IsStaff
    """

    def __call__(self, view):
        """
        Check view-level permission.

        Args:
            view: The view instance (has .request, .action, .model_admin)

        Returns:
            bool: True if permission granted
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement __call__(view)')

    def has_object_permission(self, view, obj):
        """
        Check object-level permission (optional).

        Default: Same as view-level permission (no object-specific logic).
        Override for object-specific checks.

        Args:
            view: The view instance
            obj: The model instance being accessed

        Returns:
            bool: True if permission granted
        """
        # Default: if view-level passes, object-level passes
        return self(view)

    # Composition operators
    def __and__(self, other):
        """AND composition: both must pass."""
        from djadmin.plugins.permissions.operators import And

        return And(self, other)

    def __or__(self, other):
        """OR composition: either can pass."""
        from djadmin.plugins.permissions.operators import Or

        return Or(self, other)

    def __xor__(self, other):
        """XOR composition: exactly one must pass."""
        from djadmin.plugins.permissions.operators import Xor

        return Xor(self, other)

    def __invert__(self):
        """NOT composition: invert result."""
        from djadmin.plugins.permissions.operators import Not

        return Not(self)


class AllowAny(BasePermission):
    """Allow any user (authenticated or not)."""

    def __call__(self, view):
        return True


class IsAuthenticated(BasePermission):
    """Only allow authenticated users."""

    def __call__(self, view):
        return view.request.user and view.request.user.is_authenticated


class IsStaff(BasePermission):
    """Only allow staff users (is_staff=True)."""

    def __call__(self, view):
        return view.request.user and (view.request.user.is_staff or view.request.user.is_superuser)


class IsSuperuser(BasePermission):
    """Only allow superusers."""

    def __call__(self, view):
        return view.request.user and view.request.user.is_superuser


class HasDjangoPermission(BasePermission):
    """
    Check Django model permissions.

    Supports composition for complex permission requirements:
    - HasDjangoPermission() - Auto-detect from action.django_permission_name
    - HasDjangoPermission(perm='view') - Explicit permission type
    - HasDjangoPermission(perm='webshop.change_product') - Full permission string

    Usage:
        # Auto-detect from action.django_permission_name
        permission_class = HasDjangoPermission()

        # Explicit permission type
        permission_class = HasDjangoPermission(perm='view')

        # Full permission string
        permission_class = HasDjangoPermission(perm='webshop.change_product')

        # Composition for complex requirements
        # Only users with 'view' but NOT 'change':
        permission_class = IsStaff() & HasDjangoPermission(perm='view') & ~HasDjangoPermission(perm='change')
    """

    def __init__(self, perm=None):
        """
        Args:
            perm: Optional explicit permission type or full permission string.
                  - None: Auto-detect from action.django_permission_name
                  - 'view', 'change', 'add', 'delete': Permission type
                  - 'app.perm_model': Full permission string
        """
        self.perm = perm

    def __call__(self, view):
        user = view.request.user

        # Check if user is authenticated and has permission checking capability
        if not user or not hasattr(user, 'has_perm'):
            return False

        if user.is_superuser:
            # Superuser has all permissions
            return True

        # Determine permission to check
        if self.perm is None:
            # Auto-detect from action
            if not hasattr(view, 'action') or not hasattr(view.action, 'django_permission_name'):
                return False
            perm_name = view.action.django_permission_name
        elif '.' in self.perm:
            # Full permission string provided (e.g., 'webshop.change_product')
            return user.has_perm(self.perm)
        else:
            # Permission type provided (e.g., 'view', 'change')
            perm_name = self.perm

        # Build full permission string: app_label.perm_model
        action = view.action
        model = action.model

        # If model is not set, return True since there are no model-specific permissions to check
        if model is None:
            return True

        # Construct full permission string
        required_perm = f'{model._meta.app_label}.{perm_name}_{model._meta.model_name}'

        return user.has_perm(required_perm)


class AnonReadOnly(BasePermission):
    """
    Allow any user (authenticated or not) for safe actions (view).
    Deny all unsafe actions (add, change, delete).

    Safe actions are those with django_permission_name in SAFE_PERMISSION_NAMES (default: 'view').

    This permission is designed to be composed with other permissions using OR (|):
        # Allow authenticated users for write, anyone for read
        permission_class = IsAuthenticated | AnonReadOnly

        # Allow users with Django permissions for write, anyone for read
        permission_class = HasDjangoPermission | AnonReadOnly

    Usage:
        permission_class = AnonReadOnly()
    """

    SAFE_PERMISSION_NAMES = ('view',)

    def __call__(self, view):
        """Allow if action is safe (view), deny otherwise."""
        action = view.action
        perm_name = getattr(action, 'django_permission_name', None)
        return perm_name in self.SAFE_PERMISSION_NAMES


# Convenience aliases for common patterns
# These are equivalent to the OR compositions shown above
IsAuthenticatedOrReadOnly = IsAuthenticated | AnonReadOnly
HasDjangoPermissionOrReadOnly = HasDjangoPermission | AnonReadOnly
