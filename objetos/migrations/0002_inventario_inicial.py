from django.db import migrations

INVENTARIO = [
    ("lapela", "Lapela", 1),
    ("kit_camera", "Kit de câmera", 3),
    ("drone", "Drone", 1),
    ("tripe", "Tripé", 6),
    ("filmadora", "Filmadora", 2),
]


def nomes():
    for categoria, rotulo, quantidade in INVENTARIO:
        if quantidade == 1:
            yield categoria, rotulo
        else:
            for i in range(1, quantidade + 1):
                yield categoria, f"{rotulo} {i}"


def criar(apps, schema_editor):
    Objeto = apps.get_model("objetos", "Objeto")
    for categoria, nome in nomes():
        Objeto.objects.get_or_create(nome=nome, defaults={"categoria": categoria})


def remover(apps, schema_editor):
    Objeto = apps.get_model("objetos", "Objeto")
    Objeto.objects.filter(nome__in=[nome for _, nome in nomes()]).delete()


class Migration(migrations.Migration):
    dependencies = [("objetos", "0001_initial")]

    operations = [migrations.RunPython(criar, remover)]
