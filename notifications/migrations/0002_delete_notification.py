# Generated migration to move Notification model to utils app

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        # State-only operation: tells Django the model no longer exists in notifications app
        # Database operation: empty (table should remain for utils app)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='Notification',
                ),
            ],
            database_operations=[
                # No database operations - table remains for utils app
            ],
        ),
    ]
