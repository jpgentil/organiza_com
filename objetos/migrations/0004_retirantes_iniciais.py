from django.db import migrations

RETIRANTES = [
    "Celton",
    "Luciana",
    "Wallyson",
    "Matheus",
    "Ellainy",
    "Sandro",
    "Jeovana",
    "Deboráh",
    "Wesllyn",
]


def criar(apps, schema_editor):
    Retirante = apps.get_model("objetos", "Retirante")
    for nome in RETIRANTES:
        Retirante.objects.get_or_create(nome=nome)

    # Antes, quem registrava a retirada era também o solicitante.
    Utilizacao = apps.get_model("objetos", "Utilizacao")
    for uso in Utilizacao.objects.filter(solicitante="").select_related("usuario"):
        usuario = uso.usuario
        uso.solicitante = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
        uso.save(update_fields=["solicitante"])


def remover(apps, schema_editor):
    Retirante = apps.get_model("objetos", "Retirante")
    Retirante.objects.filter(nome__in=RETIRANTES, utilizacoes__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("objetos", "0003_retirantes")]

    operations = [migrations.RunPython(criar, remover)]
