from django.db import migrations

KEY = 'orthopedic_dr_development'


def add_key(apps, schema_editor):
    AccessControl = apps.get_model('dep_admin', 'AccessControl')
    AccessControl.objects.get_or_create(key=KEY, defaults={'is_active': False})


def remove_key(apps, schema_editor):
    AccessControl = apps.get_model('dep_admin', 'AccessControl')
    AccessControl.objects.filter(key=KEY).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dep_admin', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_key, remove_key),
    ]
