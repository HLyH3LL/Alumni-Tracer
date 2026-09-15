from django.db import migrations, models


def add_created_via_voice_if_missing(apps, schema_editor):
    connection = schema_editor.connection

    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'account_furtherstudy'
              AND column_name = 'created_via_voice'
            """
        )

        if cursor.fetchone() is None:
            cursor.execute(
                """
                ALTER TABLE account_furtherstudy
                ADD COLUMN created_via_voice boolean NOT NULL DEFAULT false
                """
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_alter_activity_activity_type'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='furtherstudy',
                    name='created_via_voice',
                    field=models.BooleanField(default=False),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_created_via_voice_if_missing,
                    noop_reverse,
                ),
            ],
        ),
    ]
