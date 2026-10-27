from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DevolverForm, PegarForm, UsuarioCriarForm, UsuarioEditarForm
from .models import Objeto, Retirante, Utilizacao

admin_required = user_passes_test(lambda u: u.is_active and u.is_staff)


def nome_usuario(user):
    return user.get_full_name() or user.username


def quadro(request):
    objetos = Objeto.objects.filter(ativo=True).prefetch_related(
        Prefetch(
            "utilizacoes",
            queryset=Utilizacao.objects.select_related("usuario", "retirado_por").order_by("-retirado_em"),
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


@admin_required
def pegar(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk, ativo=True)
    if not objeto.disponivel:
        messages.error(request, f"“{objeto}” já está com {objeto.uso_atual.quem_pegou}.")
        return redirect("quadro")

    form = PegarForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                uso = Utilizacao.objects.create(objeto=objeto, usuario=request.user, **form.cleaned_data)
        except IntegrityError:
            messages.error(request, f"“{objeto}” acabou de ser entregue por outra pessoa.")
        else:
            messages.success(request, f"Entrega de “{objeto}” para {uso.quem_pegou} registrada.")
        return redirect("quadro")

    return render(request, "objetos/pegar.html", {"objeto": objeto, "form": form})


@admin_required
def devolver(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    uso = objeto.uso_atual
    if uso is None:
        messages.info(request, f"“{objeto}” já estava disponível.")
        return redirect("quadro")

    form = DevolverForm(request.POST or None, retirado_em=uso.retirado_em)
    if request.method == "POST" and form.is_valid():
        uso.devolvido_em = form.cleaned_data["devolvido_em"]
        uso.devolucao_registrada_por = request.user
        uso.save(update_fields=["devolvido_em", "devolucao_registrada_por"])
        messages.success(request, f"Devolução de “{objeto}” registrada.")
        return redirect("quadro")

    return render(request, "objetos/devolver.html", {"objeto": objeto, "uso": uso, "form": form})


@login_required
def historico(request):
    usos = Utilizacao.objects.select_related("objeto", "usuario", "retirado_por", "devolucao_registrada_por")
    objeto_id = request.GET.get("objeto") or ""
    retirante_id = request.GET.get("retirante") or ""
    if objeto_id.isdigit():
        usos = usos.filter(objeto_id=objeto_id)
    if retirante_id.isdigit():
        usos = usos.filter(retirado_por_id=retirante_id)

    pagina = Paginator(usos, 30).get_page(request.GET.get("pagina"))
    filtros = request.GET.copy()
    filtros.pop("pagina", None)
    return render(
        request,
        "objetos/historico.html",
        {
            "pagina": pagina,
            "objetos": Objeto.objects.all(),
            "retirantes": Retirante.objects.all(),
            "objeto_id": objeto_id,
            "retirante_id": retirante_id,
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
