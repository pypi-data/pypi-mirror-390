# djadmin/plugins/permissions/operators.py


def _normalize_permission(perm):
    """
    Normalize permission to an instance.

    If perm is a class, instantiate it.
    If perm is already an instance, return as-is.

    Args:
        perm: Permission class or instance

    Returns:
        Permission instance
    """
    if isinstance(perm, type):
        # It's a class, instantiate it
        return perm()
    # Already an instance
    return perm


class And:
    """
    Combine permissions with AND logic (both must pass).

    Callable: And can be called like a permission class.

    Normalizes permissions: classes are automatically instantiated.
    """

    def __init__(self, *permissions):
        # Normalize all permissions to instances
        self.permissions = [_normalize_permission(p) for p in permissions]

    def __call__(self, view):
        """Check if all permissions pass."""
        return all(perm(view) for perm in self.permissions)

    def has_object_permission(self, view, obj):
        """Check if all permissions pass for object."""
        return all(perm.has_object_permission(view, obj) for perm in self.permissions)

    # Support chaining
    def __and__(self, other):
        """Chain multiple permissions: perm1 & perm2 & perm3"""
        other = _normalize_permission(other)
        return And(*self.permissions, other)

    def __or__(self, other):
        """Combine with OR: (perm1 & perm2) | perm3"""
        other = _normalize_permission(other)
        return Or(self, other)

    def __invert__(self):
        """Negate: ~(perm1 & perm2)"""
        return Not(self)


class Or:
    """
    Combine permissions with OR logic (either can pass).

    Callable: Or can be called like a permission class.

    Normalizes permissions: classes are automatically instantiated.
    """

    def __init__(self, *permissions):
        # Normalize all permissions to instances
        self.permissions = [_normalize_permission(p) for p in permissions]

    def __call__(self, view):
        """Check if any permission passes."""
        return any(perm(view) for perm in self.permissions)

    def has_object_permission(self, view, obj):
        """Check if any permission passes for object."""
        return any(perm.has_object_permission(view, obj) for perm in self.permissions)

    # Support chaining
    def __or__(self, other):
        """Chain multiple permissions: perm1 | perm2 | perm3"""
        other = _normalize_permission(other)
        return Or(*self.permissions, other)

    def __and__(self, other):
        """Combine with AND: (perm1 | perm2) & perm3"""
        other = _normalize_permission(other)
        return And(self, other)

    def __invert__(self):
        """Negate: ~(perm1 | perm2)"""
        return Not(self)


class Not:
    """
    Invert permission result.

    Callable: Not can be called like a permission class.

    Normalizes permission: class is automatically instantiated.
    """

    def __init__(self, permission):
        # Normalize permission to instance
        self.permission = _normalize_permission(permission)

    def __call__(self, view):
        """Check if permission fails (inverted)."""
        return not self.permission(view)

    def has_object_permission(self, view, obj):
        """Check if object permission fails (inverted)."""
        return not self.permission.has_object_permission(view, obj)

    def __invert__(self):
        """Double negation: ~~perm == perm"""
        return self.permission


class Xor:
    """
    Combine permissions with XOR logic (exactly one must pass).

    Callable: Xor can be called like a permission class.

    Normalizes permissions: classes are automatically instantiated.
    """

    def __init__(self, *permissions):
        # Normalize all permissions to instances
        self.permissions = [_normalize_permission(p) for p in permissions]

    def __call__(self, view):
        """Check if exactly one permission passes."""
        results = [perm(view) for perm in self.permissions]
        return results.count(True) == 1

    def has_object_permission(self, view, obj):
        """Check if exactly one permission passes for object."""
        results = [perm.has_object_permission(view, obj) for perm in self.permissions]
        return results.count(True) == 1

    # Support chaining
    def __xor__(self, other):
        """Chain multiple permissions: perm1 ^ perm2 ^ perm3"""
        other = _normalize_permission(other)
        return Xor(*self.permissions, other)

    def __and__(self, other):
        """Combine with AND: (perm1 ^ perm2) & perm3"""
        other = _normalize_permission(other)
        return And(self, other)

    def __or__(self, other):
        """Combine with OR: (perm1 ^ perm2) | perm3"""
        other = _normalize_permission(other)
        return Or(self, other)

    def __invert__(self):
        """Negate: ~(perm1 ^ perm2)"""
        return Not(self)
