from django.contrib.auth.models import Group

def create_user_group():
    group, created = Group.objects.get_or_create(name='user')
    if created:
        print('Grupo "user" criado.')
    else:
        print('Grupo "user" já existe.')



create_user_group()