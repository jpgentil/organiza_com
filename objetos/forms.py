from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class PegarForm(forms.Form):
    motivo = forms.CharField(
        label="Motivo",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Ex.: cobertura do evento X no auditório"}),
        max_length=500,
    )


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
