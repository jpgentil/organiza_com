from django.contrib import admin

from .models import Objeto, Utilizacao


class UtilizacaoInline(admin.TabularInline):
    model = Utilizacao
    extra = 0
    fields = ["usuario", "motivo", "retirado_em", "devolvido_em"]
    readonly_fields = ["retirado_em"]
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
        return f"Em uso por {uso.usuario.get_full_name() or uso.usuario}" if uso else "Disponível"


@admin.register(Utilizacao)
class UtilizacaoAdmin(admin.ModelAdmin):
    list_display = ["objeto", "usuario", "motivo", "retirado_em", "devolvido_em"]
    list_filter = ["objeto__categoria", "objeto", "usuario"]
    search_fields = ["objeto__nome", "usuario__username", "usuario__first_name", "motivo"]
    date_hierarchy = "retirado_em"
    list_select_related = ["objeto", "usuario"]
