from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def setup_groups():
    # Create Viewer group
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')

    # Manually create a ContentType for Cliente (since it's SQLAlchemy)
    content_type, _ = ContentType.objects.get_or_create(
        app_label='core',  # Must match your app name
        model='cliente'    # Lowercase model name
    )

    # Define and assign the permission
    view_perm, _ = Permission.objects.get_or_create(
        codename='can_view_item',
        name='Can view item',
        content_type=content_type,
    )
    viewer_group.permissions.set([view_perm])

# Run this in shell:
# python manage.py shell
# >>> from apps.users.admin import setup_groups; setup_groups()
