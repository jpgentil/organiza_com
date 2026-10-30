from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.quadro, name="quadro"),
    path("login/", views.Entrar.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("objeto/<int:pk>/pegar/", views.pegar, name="pegar"),
    path("objeto/<int:pk>/devolver/", views.devolver, name="devolver"),
    path("historico/", views.historico, name="historico"),
    path("gestao/usuarios/", views.usuarios, name="usuarios"),
    path("gestao/usuarios/novo/", views.usuario_criar, name="usuario_criar"),
    path("gestao/usuarios/<int:pk>/", views.usuario_editar, name="usuario_editar"),
]
