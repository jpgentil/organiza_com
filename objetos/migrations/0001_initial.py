import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Objeto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, unique=True, verbose_name="nome")),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("lapela", "Lapela"),
                            ("kit_camera", "Kit de câmera"),
                            ("drone", "Drone"),
                            ("tripe", "Tripé"),
                            ("filmadora", "Filmadora"),
                            ("outro", "Outro"),
                        ],
                        default="outro",
                        max_length=20,
                        verbose_name="categoria",
                    ),
                ),
                ("descricao", models.TextField(blank=True, verbose_name="descrição")),
                ("patrimonio", models.CharField(blank=True, max_length=50, verbose_name="nº de patrimônio")),
                ("foto", models.ImageField(blank=True, upload_to="objetos/", verbose_name="foto")),
                (
                    "ativo",
                    models.BooleanField(
                        default=True,
                        help_text="Desmarque para retirar o objeto do quadro sem apagar o histórico.",
                        verbose_name="ativo",
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
            ],
            options={
                "verbose_name": "objeto",
                "verbose_name_plural": "objetos",
                "ordering": ["categoria", "nome"],
            },
        ),
        migrations.CreateModel(
            name="Utilizacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("motivo", models.TextField(verbose_name="motivo")),
                ("retirado_em", models.DateTimeField(auto_now_add=True, verbose_name="retirado em")),
                ("devolvido_em", models.DateTimeField(blank=True, null=True, verbose_name="devolvido em")),
                (
                    "objeto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="utilizacoes",
                        to="objetos.objeto",
                        verbose_name="objeto",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="utilizacoes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="utilizador",
                    ),
                ),
            ],
            options={
                "verbose_name": "utilização",
                "verbose_name_plural": "utilizações",
                "ordering": ["-retirado_em"],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("devolvido_em__isnull", True)),
                        fields=("objeto",),
                        name="um_uso_aberto_por_objeto",
                        violation_error_message="Este objeto já está em uso.",
                    )
                ],
            },
        ),
    ]
