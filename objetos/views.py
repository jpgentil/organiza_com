from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import PegarForm, UsuarioCriarForm, UsuarioEditarForm
from .models import Objeto, Utilizacao

admin_required = user_passes_test(lambda u: u.is_active and u.is_staff)


def nome_usuario(user):
    return user.get_full_name() or user.username


def quadro(request):
    objetos = Objeto.objects.filter(ativo=True).prefetch_related(
        Prefetch(
            "utilizacoes",
            queryset=Utilizacao.objects.select_related("usuario").order_by("-retirado_em"),
            to_attr="utilizacoes_ordenadas",
        )
    )
    disponiveis, indisponiveis = [], []
    for objeto in objetos:
        (disponiveis if objeto.disponivel else indisponiveis).append(objeto)
    return render(
        request,
        "objetos/quadro.html",
        {"disponiveis": disponiveis, "indisponiveis": indisponiveis},
    )


@login_required
def pegar(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk, ativo=True)
    if not objeto.disponivel:
        messages.error(request, f"“{objeto}” já está em uso por {nome_usuario(objeto.uso_atual.usuario)}.")
        return redirect("quadro")

    form = PegarForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                Utilizacao.objects.create(
                    objeto=objeto, usuario=request.user, motivo=form.cleaned_data["motivo"]
                )
        except IntegrityError:
            messages.error(request, f"“{objeto}” acabou de ser pego por outra pessoa.")
        else:
            messages.success(request, f"Você pegou “{objeto}”. Lembre-se de devolver no sistema.")
        return redirect("quadro")

    return render(request, "objetos/pegar.html", {"objeto": objeto, "form": form})


@login_required
@require_POST
def devolver(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    uso = objeto.uso_atual
    if uso is None:
        messages.info(request, f"“{objeto}” já estava disponível.")
    elif uso.usuario_id != request.user.pk and not request.user.is_staff:
        messages.error(request, "Só quem pegou o objeto (ou um administrador) pode devolvê-lo.")
    else:
        uso.devolvido_em = timezone.now()
        uso.save(update_fields=["devolvido_em"])
        messages.success(request, f"“{objeto}” foi devolvido.")
    return redirect("quadro")


@login_required
def historico(request):
    usos = Utilizacao.objects.select_related("objeto", "usuario")
    objeto_id = request.GET.get("objeto") or ""
    usuario_id = request.GET.get("usuario") or ""
    if objeto_id.isdigit():
        usos = usos.filter(objeto_id=objeto_id)
    if usuario_id.isdigit():
        usos = usos.filter(usuario_id=usuario_id)

    pagina = Paginator(usos, 30).get_page(request.GET.get("pagina"))
    filtros = request.GET.copy()
    filtros.pop("pagina", None)
    return render(
        request,
        "objetos/historico.html",
        {
            "pagina": pagina,
            "objetos": Objeto.objects.all(),
            "usuarios": User.objects.order_by("first_name", "username"),
            "objeto_id": objeto_id,
            "usuario_id": usuario_id,
            "filtros": filtros.urlencode(),
        },
    )


@admin_required
def usuarios(request):
    return render(
        request,
        "objetos/gerenciar_usuarios.html",
        {"usuarios": User.objects.order_by("-is_active", "first_name", "username")},
    )


@admin_required
def usuario_criar(request):
    form = UsuarioCriarForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Usuário “{nome_usuario(user)}” cadastrado.")
        return redirect("usuarios")
    return render(request, "objetos/usuario_form.html", {"form": form, "titulo": "Cadastrar usuário"})


@admin_required
def usuario_editar(request, pk):
    alvo = get_object_or_404(User, pk=pk)
    if alvo.is_superuser and not request.user.is_superuser:
        messages.error(request, "Apenas o administrador principal pode editar este usuário.")
        return redirect("usuarios")
    form = UsuarioEditarForm(request.POST or None, instance=alvo, editor=request.user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Usuário “{nome_usuario(user)}” atualizado.")
        return redirect("usuarios")
    return render(
        request,
        "objetos/usuario_form.html",
        {"form": form, "titulo": f"Editar “{nome_usuario(alvo)}”"},
    )
