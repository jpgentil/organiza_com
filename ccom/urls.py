from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "CCOM · Controle de Objetos"
admin.site.site_title = "CCOM · Controle de Objetos"
admin.site.index_title = "Administração"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("objetos.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
