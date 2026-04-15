from django.db import migrations, models


def set_existing_users_verified(apps, schema_editor):
    User = apps.get_model('custom_user', 'User')
    User.objects.all().update(email_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0002_user_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_existing_users_verified, migrations.RunPython.noop),
    ]
