"""
Django management command to wait for the database to be available.
Useful in Docker environments where the web service might start before PostgreSQL is ready.
"""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database to be available"""

    help = 'Wait for database to be available'

    def handle(self, *args, **options):
        """Handle the command - poll database until it's available"""
        self.stdout.write('Waiting for database...')
        db_conn = None
        max_retries = 30
        retry_count = 0

        while not db_conn and retry_count < max_retries:
            try:
                # Try to get database connection
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS('Database available!'))
            except OperationalError:
                retry_count += 1
                self.stdout.write(f'Database unavailable, waiting 1 second... (attempt {retry_count}/{max_retries})')
                time.sleep(1)

        if not db_conn:
            self.stdout.write(self.style.ERROR('Database connection failed after maximum retries'))
            raise OperationalError('Could not connect to database')
