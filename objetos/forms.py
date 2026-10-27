from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from .models import Retirante

FORMATO_DATA_HORA = "%Y-%m-%dT%H:%M"


def campo_data_hora(label):
    return forms.DateTimeField(
        label=label,
        initial=lambda: timezone.localtime().replace(second=0, microsecond=0),
        input_formats=[FORMATO_DATA_HORA],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format=FORMATO_DATA_HORA),
    )


def validar_nao_futuro(momento):
    # Tolera o minuto corrente, já que o campo não tem segundos.
    if momento > timezone.now() + timedelta(minutes=1):
        raise forms.ValidationError("O horário não pode estar no futuro.")
    return momento


class PegarForm(forms.Form):
    solicitante = forms.CharField(
        label="Solicitante",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Quem pediu o objeto"}),
    )
    retirado_por = forms.ModelChoiceField(
        label="Quem pegou",
        queryset=Retirante.objects.filter(ativo=True),
        empty_label="Selecione…",
    )
    retirado_em = campo_data_hora("Horário da retirada")
    motivo = forms.CharField(
        label="Motivo",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Ex.: cobertura do evento X no auditório"}),
        max_length=500,
    )

    def clean_retirado_em(self):
        return validar_nao_futuro(self.cleaned_data["retirado_em"])


class DevolverForm(forms.Form):
    devolvido_em = campo_data_hora("Horário da devolução")

    def __init__(self, *args, retirado_em, **kwargs):
        super().__init__(*args, **kwargs)
        self.retirado_em = retirado_em

    def clean_devolvido_em(self):
        devolvido_em = validar_nao_futuro(self.cleaned_data["devolvido_em"])
        if devolvido_em < self.retirado_em.replace(second=0, microsecond=0):
            raise forms.ValidationError("A devolução não pode ser anterior à retirada.")
        return devolvido_em


class UsuarioCriarForm(UserCreationForm):
    is_staff = forms.BooleanField(label="É administrador", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        labels = {"first_name": "Nome", "last_name": "Sobrenome", "username": "Usuário (login)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data["is_staff"]
        if commit:
            user.save()
        return user


class UsuarioEditarForm(forms.ModelForm):
    nova_senha = forms.CharField(
        label="Nova senha",
        required=False,
        widget=forms.PasswordInput,
        help_text="Deixe em branco para manter a senha atual.",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "is_staff", "is_active"]
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "username": "Usuário (login)",
            "is_staff": "É administrador",
            "is_active": "Ativo",
        }
        help_texts = {
            "username": "",
            "is_staff": "",
            "is_active": "Desmarque para bloquear o acesso sem apagar o histórico.",
        }

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.editor = editor

    def clean(self):
        cleaned = super().clean()
        if self.editor is not None and self.instance.pk == self.editor.pk:
            if not cleaned.get("is_staff") or not cleaned.get("is_active"):
                raise forms.ValidationError(
                    "Você não pode remover seu próprio acesso de administrador ou desativar a si mesmo."
                )
        return cleaned

    def clean_nova_senha(self):
        senha = self.cleaned_data.get("nova_senha")
        if senha:
            validate_password(senha, self.instance)
        return senha

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("nova_senha"):
            user.set_password(self.cleaned_data["nova_senha"])
        if commit:
            user.save()
        return user
