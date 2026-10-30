from django.db import migrations

RETIRANTES = ["Valdir", "Diego", "Jair", "Walber"]


def criar(apps, schema_editor):
    Retirante = apps.get_model("objetos", "Retirante")
    for nome in RETIRANTES:
        Retirante.objects.get_or_create(nome=nome)


def remover(apps, schema_editor):
    Retirante = apps.get_model("objetos", "Retirante")
    Retirante.objects.filter(nome__in=RETIRANTES, utilizacoes__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("objetos", "0005_inventario_completo")]

    operations = [migrations.RunPython(criar, remover)]
