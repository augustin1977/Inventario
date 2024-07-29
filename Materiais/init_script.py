from usuarios.models import *

def criando_ambiente():
    usuario, created = Tipo.objects.get_or_create(tipo='user')
    admin, created = Tipo.objects.get_or_create(tipo='admin')
    system,created= Usuario.objects.get_or_create(nome="System",
                    email="inventariomte@gmail.com",
                    tipo= admin,
                    ativo=True,
                    primeiro_acesso=True)
    usuario.save()
    admin.save()
    system.save()
    


