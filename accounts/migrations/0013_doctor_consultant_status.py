from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_rolepagesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultant',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consultant',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='doctor',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='doctor',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]