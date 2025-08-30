"""
Management command to setup the database for production deployment
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction


class Command(BaseCommand):
    help = 'Setup database for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a default superuser',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up database...'))
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=1)
        
        # Create superuser if requested
        if options['create_superuser']:
            self.stdout.write('Creating superuser...')
            User = get_user_model()
            
            try:
                with transaction.atomic():
                    if not User.objects.filter(email='admin@example.com').exists():
                        User.objects.create_superuser(
                            email='admin@example.com',
                            password='admin123',
                            full_name='Admin User'
                        )
                        self.stdout.write(
                            self.style.SUCCESS('Superuser created successfully!')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING('Superuser already exists.')
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating superuser: {e}')
                )
        
        # Collect static files
        self.stdout.write('Collecting static files...')
        call_command('collectstatic', interactive=False, verbosity=1)
        
        self.stdout.write(
            self.style.SUCCESS('Database setup completed successfully!')
        )
