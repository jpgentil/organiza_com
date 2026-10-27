from django.contrib import admin

from .models import Objeto, Retirante, Utilizacao


class UtilizacaoInline(admin.TabularInline):
    model = Utilizacao
    extra = 0
    fields = ["solicitante", "retirado_por", "motivo", "retirado_em", "devolvido_em", "usuario", "devolucao_registrada_por"]
    ordering = ["-retirado_em"]


@admin.register(Objeto)
class ObjetoAdmin(admin.ModelAdmin):
    list_display = ["nome", "categoria", "patrimonio", "situacao", "ativo"]
    list_filter = ["categoria", "ativo"]
    search_fields = ["nome", "patrimonio", "descricao"]
    inlines = [UtilizacaoInline]

    @admin.display(description="situação")
    def situacao(self, obj):
        uso = obj.uso_atual
        return f"Com {uso.quem_pegou}" if uso else "Disponível"


@admin.register(Retirante)
class RetiranteAdmin(admin.ModelAdmin):
    list_display = ["nome", "ativo"]
    list_editable = ["ativo"]
    search_fields = ["nome"]


@admin.register(Utilizacao)
class UtilizacaoAdmin(admin.ModelAdmin):
    list_display = ["objeto", "solicitante", "retirado_por", "motivo", "retirado_em", "devolvido_em", "usuario"]
    list_filter = ["objeto__categoria", "objeto", "retirado_por"]
    search_fields = ["objeto__nome", "solicitante", "retirado_por__nome", "usuario__username", "usuario__first_name", "motivo"]
    date_hierarchy = "retirado_em"
    list_select_related = ["objeto", "retirado_por", "usuario"]
