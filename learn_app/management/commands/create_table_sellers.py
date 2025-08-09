from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Create property table if not exists using raw SQL'

    def handle(self, *args, **kwargs):
        sql = """
        CREATE TABLE IF NOT EXISTS property (
            id SERIAL PRIMARY KEY,
            area_location VARCHAR(255) NOT NULL,
            property_type VARCHAR(20) NOT NULL,
            rent NUMERIC(10,2) NOT NULL,
            contact_number VARCHAR(20) NOT NULL,
            description TEXT,
            posted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
        self.stdout.write(self.style.SUCCESS("✅ Property table ensured in DB"))
