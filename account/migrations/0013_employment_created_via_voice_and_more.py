from django.db import migrations, models


def add_voice_fields_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor

    if vendor != "postgresql":
        return

    with connection.cursor() as cursor:

        # Employment: created_via_voice
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'account_employment'
              AND column_name = 'created_via_voice'
            """
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                ALTER TABLE account_employment
                ADD COLUMN created_via_voice boolean NOT NULL DEFAULT false
                """
            )

        # Employment: voice_transcript
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'account_employment'
              AND column_name = 'voice_transcript'
            """
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                ALTER TABLE account_employment
                ADD COLUMN voice_transcript text NULL
                """
            )

        # Employment: voice_updated
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'account_employment'
              AND column_name = 'voice_updated'
            """
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                ALTER TABLE account_employment
                ADD COLUMN voice_updated boolean NOT NULL DEFAULT false
                """
            )

        # FurtherStudy: created_via_voice
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

        # FurtherStudy: voice_transcript
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'account_furtherstudy'
              AND column_name = 'voice_transcript'
            """
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                ALTER TABLE account_furtherstudy
                ADD COLUMN voice_transcript text NULL
                """
            )

        # FurtherStudy: voice_updated
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'account_furtherstudy'
              AND column_name = 'voice_updated'
            """
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                ALTER TABLE account_furtherstudy
                ADD COLUMN voice_updated boolean NOT NULL DEFAULT false
                """
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_merge_20260405_0327'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='employment',
                    name='created_via_voice',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='employment',
                    name='voice_transcript',
                    field=models.TextField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='employment',
                    name='voice_updated',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='furtherstudy',
                    name='created_via_voice',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='furtherstudy',
                    name='voice_transcript',
                    field=models.TextField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='furtherstudy',
                    name='voice_updated',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='siteconfig',
                    name='favicon',
                    field=models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='logos/',
                    ),
                ),
                migrations.AddField(
                    model_name='siteconfig',
                    name='logo_footer',
                    field=models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='logos/',
                    ),
                ),
                migrations.AddField(
                    model_name='siteconfig',
                    name='logo_main',
                    field=models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='logos/',
                    ),
                ),
                migrations.AlterField(
                    model_name='activity',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='alumni',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='announcement',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='carouselslide',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='corevalue',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='employment',
                    name='date_left',
                    field=models.DateField(blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name='employment',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='employmentstatus',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='feature',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='furtherstudy',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='pagecontent',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='program',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='registrationpagecontent',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='siteconfig',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_voice_fields_if_missing,
                    noop_reverse,
                ),
            ],
        ),
    ]
