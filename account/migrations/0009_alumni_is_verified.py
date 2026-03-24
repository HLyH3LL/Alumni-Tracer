# Adds account_alumni.is_verified if missing (handles DBs updated outside Django).

from django.db import migrations, models


def add_is_verified_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor
    with connection.cursor() as cursor:
        if vendor == "postgresql":
            cursor.execute(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'account_alumni'
                  AND column_name = 'is_verified'
                """
            )
            if cursor.fetchone():
                return
            cursor.execute(
                "ALTER TABLE account_alumni ADD COLUMN is_verified boolean NOT NULL DEFAULT false"
            )
            return

        if vendor == "sqlite":
            cursor.execute("PRAGMA table_info(account_alumni);")
            if any(row[1] == "is_verified" for row in cursor.fetchall()):
                return
            cursor.execute(
                "ALTER TABLE account_alumni ADD COLUMN is_verified bool NOT NULL DEFAULT 0"
            )
            return

        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'account_alumni'
                  AND COLUMN_NAME = 'is_verified'
                """
            )
            if cursor.fetchone()[0]:
                return
            cursor.execute(
                "ALTER TABLE account_alumni ADD COLUMN is_verified bool NOT NULL DEFAULT 0"
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0008_employment_created_via_voice_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="alumni",
                    name="is_verified",
                    field=models.BooleanField(
                        default=False,
                        help_text="Set True when alumni information is verified (e.g. by admin).",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(add_is_verified_if_missing, noop_reverse),
            ],
        ),
    ]
