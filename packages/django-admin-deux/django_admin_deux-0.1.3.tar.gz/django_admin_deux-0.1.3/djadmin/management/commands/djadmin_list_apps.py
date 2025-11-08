"""Management command to list INSTALLED_APPS from djadmin_apps()."""

from django.core.management.base import BaseCommand

from djadmin import djadmin_apps


class Command(BaseCommand):
    help = 'List INSTALLED_APPS provided by djadmin_apps() for manual configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['python', 'list', 'json'],
            default='python',
            help='Output format (default: python)',
        )
        parser.add_argument(
            '--quote',
            type=str,
            choices=['single', 'double'],
            default='single',
            help='Quote style for python format (default: single)',
        )

    def handle(self, *args, **options):
        """Output the apps list in the requested format."""
        apps = djadmin_apps()
        format_type = options['format']
        quote_style = options['quote']

        if format_type == 'python':
            self._output_python(apps, quote_style)
        elif format_type == 'list':
            self._output_list(apps)
        elif format_type == 'json':
            self._output_json(apps)

    def _output_python(self, apps, quote_style):
        """Output as Python list for copy/paste into settings.py."""
        quote = "'" if quote_style == 'single' else '"'

        self.stdout.write(self.style.SUCCESS('\n# Add to INSTALLED_APPS in settings.py:'))
        self.stdout.write('INSTALLED_APPS = [')
        self.stdout.write('    # ... your other apps ...')

        for app in apps:
            self.stdout.write(f'    {quote}{app}{quote},')

        self.stdout.write(']')
        self.stdout.write('')

    def _output_list(self, apps):
        """Output as simple list (one per line)."""
        self.stdout.write(self.style.SUCCESS('\ndjadmin_apps() returns:'))
        for i, app in enumerate(apps, 1):
            self.stdout.write(f'{i}. {app}')
        self.stdout.write(f'\nTotal: {len(apps)} apps\n')

    def _output_json(self, apps):
        """Output as JSON array."""
        import json

        self.stdout.write(json.dumps(apps, indent=2))
