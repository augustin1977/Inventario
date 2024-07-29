from django.core.management import BaseCommand
from Materiais import init_script

class Command(BaseCommand):
    help = 'executa a carga inicial do sistema'

    def handle(self, *args, **kwargs):
        init_script.criando_ambiente()
        