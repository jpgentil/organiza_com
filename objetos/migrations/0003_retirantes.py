import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("objetos", "0002_inventario_inicial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Retirante",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, unique=True, verbose_name="nome")),
                (
                    "ativo",
                    models.BooleanField(
                        default=True,
                        help_text="Desmarque para tirar o nome da lista sem apagar o histórico.",
                        verbose_name="ativo",
                    ),
                ),
            ],
            options={"verbose_name": "retirante", "verbose_name_plural": "retirantes", "ordering": ["nome"]},
        ),
        migrations.AlterField(
            model_name="utilizacao",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="utilizacoes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="entrega registrada por",
            ),
        ),
        migrations.AddField(
            model_name="utilizacao",
            name="solicitante",
            field=models.CharField(default="", max_length=150, verbose_name="solicitante"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="utilizacao",
            name="retirado_por",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="utilizacoes",
                to="objetos.retirante",
                verbose_name="quem pegou",
            ),
        ),
        migrations.AlterField(
            model_name="utilizacao",
            name="retirado_em",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="retirado em"),
        ),
        migrations.AddField(
            model_name="utilizacao",
            name="devolucao_registrada_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="devolucoes_registradas",
                to=settings.AUTH_USER_MODEL,
                verbose_name="devolução registrada por",
            ),
        ),
    ]
