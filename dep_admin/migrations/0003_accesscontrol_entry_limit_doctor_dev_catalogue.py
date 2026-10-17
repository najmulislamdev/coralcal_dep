from django.db import migrations, models

KEY = 'doctor_dev_catalogue'


def add_key(apps, schema_editor):
    AccessControl = apps.get_model('dep_admin', 'AccessControl')
    AccessControl.objects.get_or_create(key=KEY, defaults={'is_active': False, 'entry_limit': 1})


def remove_key(apps, schema_editor):
    AccessControl = apps.get_model('dep_admin', 'AccessControl')
    AccessControl.objects.filter(key=KEY).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dep_admin', '0002_orthopedic_dr_development_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesscontrol',
            name='entry_limit',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(add_key, remove_key),
    ]
