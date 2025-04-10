from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def setup_groups():
    # Viewer group (existing)
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')
    # Editor group
    editor_group, _ = Group.objects.get_or_create(name='Editor')

    # Manually create ContentType for Cliente
    content_type, _ = ContentType.objects.get_or_create(
        app_label='core',
        model='cliente'
    )

    # Viewer permission
    view_perm, _ = Permission.objects.get_or_create(
        codename='can_view_item',
        name='Can view item',
        content_type=content_type,
    )
    viewer_group.permissions.set([view_perm])

    # Editor permission
    edit_perm, _ = Permission.objects.get_or_create(
        codename='can_edit_item',
        name='Can edit item',
        content_type=content_type,
    )
    editor_group.permissions.set([edit_perm, view_perm])  # Editors can view too

# Run: python manage.py shell
# >>> from apps.users.admin import setup_groups; setup_groups()
