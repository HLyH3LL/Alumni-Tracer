
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_alter_alumni_profile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='employment',
            name='date_left',
            field=models.DateField(blank=True, null=True),
        ),
    ]