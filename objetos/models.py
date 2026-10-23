from django.conf import settings
from django.db import models
from django.db.models import Q


class Objeto(models.Model):
    class Categoria(models.TextChoices):
        LAPELA = "lapela", "Lapela"
        KIT_CAMERA = "kit_camera", "Kit de câmera"
        DRONE = "drone", "Drone"
        TRIPE = "tripe", "Tripé"
        FILMADORA = "filmadora", "Filmadora"
        OUTRO = "outro", "Outro"

    nome = models.CharField("nome", max_length=100, unique=True)
    categoria = models.CharField(
        "categoria", max_length=20, choices=Categoria.choices, default=Categoria.OUTRO
    )
    descricao = models.TextField("descrição", blank=True)
    patrimonio = models.CharField("nº de patrimônio", max_length=50, blank=True)
    foto = models.ImageField("foto", upload_to="objetos/", blank=True)
    ativo = models.BooleanField(
        "ativo", default=True, help_text="Desmarque para retirar o objeto do quadro sem apagar o histórico."
    )
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "objeto"
        verbose_name_plural = "objetos"
        ordering = ["categoria", "nome"]

    def __str__(self):
        return self.nome

    def _utilizacoes(self):
        # Usa a lista pré-carregada pelo quadro (prefetch) quando disponível.
        if hasattr(self, "utilizacoes_ordenadas"):
            return self.utilizacoes_ordenadas
        return list(self.utilizacoes.select_related("usuario").order_by("-retirado_em"))

    @property
    def uso_atual(self):
        return next((u for u in self._utilizacoes() if u.devolvido_em is None), None)

    @property
    def ultimo_uso(self):
        return next((u for u in self._utilizacoes() if u.devolvido_em is not None), None)

    @property
    def disponivel(self):
        return self.uso_atual is None


class Utilizacao(models.Model):
    objeto = models.ForeignKey(
        Objeto, on_delete=models.CASCADE, related_name="utilizacoes", verbose_name="objeto"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="utilizacoes",
        verbose_name="utilizador",
    )
    motivo = models.TextField("motivo")
    retirado_em = models.DateTimeField("retirado em", auto_now_add=True)
    devolvido_em = models.DateTimeField("devolvido em", null=True, blank=True)

    class Meta:
        verbose_name = "utilização"
        verbose_name_plural = "utilizações"
        ordering = ["-retirado_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["objeto"],
                condition=Q(devolvido_em__isnull=True),
                name="um_uso_aberto_por_objeto",
                violation_error_message="Este objeto já está em uso.",
            )
        ]

    def __str__(self):
        return f"{self.objeto} — {self.usuario}"
