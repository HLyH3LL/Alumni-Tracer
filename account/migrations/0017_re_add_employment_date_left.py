from django.db import migrations, models


def add_date_left_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor

    with connection.cursor() as cursor:
        if vendor == "postgresql":
            cursor.execute(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'account_employment'
                  AND column_name = 'date_left'
                """
            )

            if cursor.fetchone():
                return

            cursor.execute(
                """
                ALTER TABLE account_employment
                ADD COLUMN date_left date NULL
                """
            )
            return

        if vendor == "sqlite":
            cursor.execute("PRAGMA table_info(account_employment);")

            if any(row[1] == "date_left" for row in cursor.fetchall()):
                return

            cursor.execute(
                """
                ALTER TABLE account_employment
                ADD COLUMN date_left date NULL
                """
            )
            return

        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'account_employment'
                  AND COLUMN_NAME = 'date_left'
                """
            )

            if cursor.fetchone()[0]:
                return

            cursor.execute(
                """
                ALTER TABLE account_employment
                ADD COLUMN date_left date NULL
                """
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0016_alter_alumni_profile_photo"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="employment",
                    name="date_left",
                    field=models.DateField(
                        blank=True,
                        null=True,
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_date_left_if_missing,
                    noop_reverse,
                ),
            ],
        ),
    ]
