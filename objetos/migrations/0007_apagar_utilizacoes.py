from django.db import migrations


def apagar(apps, schema_editor):
    # Exclusão definitiva: reverter esta migração não recupera os registros.
    apps.get_model("objetos", "Utilizacao").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("objetos", "0006_novos_retirantes")]

    operations = [migrations.RunPython(apagar, migrations.RunPython.noop)]
