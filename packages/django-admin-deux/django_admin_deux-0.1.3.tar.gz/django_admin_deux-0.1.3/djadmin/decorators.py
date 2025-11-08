from djadmin.sites import site as default_site


def register(*models, site=None, override=False):
    """
    Decorator for registering models with admin.

    Usage:
        @register(MyModel)
        class MyModelAdmin(ModelAdmin):
            list_display = ['name']

    Or with custom site:
        @register(MyModel, site=custom_site)
        class MyModelAdmin(ModelAdmin):
            pass

    Or with override to replace existing registrations:
        @register(MyModel, override=True)
        class MyModelAdmin(ModelAdmin):
            pass
    """

    def _wrapper(admin_class):
        if not models:
            raise ValueError('At least one model must be specified')

        admin_site = site if site is not None else default_site

        for model in models:
            admin_site.register(model, admin_class, override=override)

        return admin_class

    return _wrapper
