from django.db import migrations

class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        # This SQL command enables the extension for this database
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS btree_gist;",
            "DROP EXTENSION IF EXISTS btree_gist;",
        )
    ]
