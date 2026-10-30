from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import FORMATO_DATA_HORA
from .models import Objeto, Retirante, Utilizacao


def data_hora(momento):
    return timezone.localtime(momento).strftime(FORMATO_DATA_HORA)


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123", first_name="Maria")
        self.outro = User.objects.create_user("joao", password="senha-forte-123", first_name="João")
        self.admin = User.objects.create_user("chefe", password="senha-forte-123", is_staff=True)
        self.tripe = Objeto.objects.get(nome="Tripé de celular com suporte 1")
        self.matheus = Retirante.objects.get(nome="Matheus")
        self.sandro = Retirante.objects.get(nome="Sandro")

    def usar(self, retirante, **kwargs):
        return Utilizacao.objects.create(
            objeto=self.tripe, usuario=self.admin, solicitante="Fulano", retirado_por=retirante, motivo="x", **kwargs
        )


class InventarioTests(TestCase):
    def test_inventario(self):
        ativos = Objeto.objects.filter(ativo=True)
        self.assertEqual(ativos.count(), 55)
        self.assertEqual(ativos.filter(categoria="camera").count(), 3)
        self.assertEqual(ativos.filter(categoria="carregador").count(), 10)
        self.assertEqual(ativos.filter(categoria="tripe").count(), 8)
        self.assertEqual(ativos.filter(categoria="lapela").count(), 6)
        self.assertTrue(ativos.filter(nome="Drone DJI Air 2S").exists())
        self.assertTrue(ativos.filter(nome="Câmera Canon 5D Mark IV 3").exists())

    def test_inventario_antigo(self):
        self.assertFalse(Objeto.objects.filter(nome__in=["Drone", "Kit de câmera 1"]).exists())
        self.assertEqual(Objeto.objects.filter(nome__startswith="Tripé ", ativo=False).count(), 6)

    def test_retirantes_iniciais(self):
        self.assertEqual(
            set(Retirante.objects.values_list("nome", flat=True)),
            {
                "Celton", "Luciana", "Wallyson", "Matheus", "Ellainy", "Sandro", "Jeovana", "Deboráh", "Wesllyn",
                "Valdir", "Diego", "Jair", "Walber",
            },
        )


class LoginTests(BaseTestCase):
    def entrar(self, **dados):
        return self.client.post(reverse("login"), {"username": "maria", "password": "senha-forte-123", **dados})

    def test_manter_conectado_mantem_sessao_por_30_dias(self):
        self.assertRedirects(self.entrar(manter_conectado="on"), reverse("quadro"))
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.session.get_expiry_age(), 60 * 60 * 24 * 30)
        self.assertEqual(self.client.cookies["sessionid"]["max-age"], 60 * 60 * 24 * 30)

    def test_sem_manter_conectado_expira_ao_fechar_navegador(self):
        self.assertRedirects(self.entrar(), reverse("quadro"))
        self.assertTrue(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.cookies["sessionid"]["max-age"], "")


class QuadroTests(BaseTestCase):
    def test_quadro_publico_sem_botoes(self):
        resp = self.client.get(reverse("quadro"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["disponiveis"]), 55)
        self.assertNotContains(resp, "Pegar</a>")

    def test_quadro_mostra_quem_esta_com_objeto(self):
        Utilizacao.objects.create(
            objeto=self.tripe, usuario=self.admin, solicitante="Maria Souza", retirado_por=self.matheus,
            motivo="Evento no auditório",
        )
        resp = self.client.get(reverse("quadro"))
        self.assertEqual([o.nome for o in resp.context["indisponiveis"]], ["Tripé de celular com suporte 1"])
        self.assertContains(resp, "Matheus")
        self.assertContains(resp, "Maria Souza")
        self.assertContains(resp, "Evento no auditório")

    def test_utilizador_comum_nao_ve_botoes(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("quadro"))
        self.assertNotContains(resp, "Pegar</a>")
        self.usar(self.matheus)
        self.assertNotContains(self.client.get(reverse("quadro")), "Devolver</a>")

    def test_registro_antigo_usa_usuario_como_quem_pegou(self):
        uso = Utilizacao.objects.create(objeto=self.tripe, usuario=self.user, solicitante="Maria", motivo="x")
        self.assertEqual(uso.quem_pegou, "Maria")


class PegarDevolverTests(BaseTestCase):
    def test_pegar_exige_login(self):
        resp = self.client.get(reverse("pegar", args=[self.tripe.pk]))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('pegar', args=[self.tripe.pk])}")

    def test_utilizador_comum_nao_registra(self):
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("pegar", args=[self.tripe.pk]),
            {"retirado_por": self.matheus.pk, "retirado_em": data_hora(timezone.now()), "motivo": "y"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(self.tripe.disponivel)

        self.usar(self.matheus)
        self.client.post(reverse("devolver", args=[self.tripe.pk]), {"devolvido_em": data_hora(timezone.now())})
        self.assertFalse(self.tripe.disponivel)

    def test_admin_registra_entrega_e_devolucao(self):
        self.client.force_login(self.admin)
        retirada = timezone.now() - timedelta(hours=3)
        self.client.post(
            reverse("pegar", args=[self.tripe.pk]),
            {"retirado_por": self.matheus.pk, "retirado_em": data_hora(retirada), "motivo": "Gravação"},
        )
        uso = self.tripe.uso_atual
        self.assertEqual(
            (uso.solicitante, uso.retirado_por, uso.motivo, uso.usuario),
            ("chefe", self.matheus, "Gravação", self.admin),
        )
        self.assertEqual(data_hora(uso.retirado_em), data_hora(retirada))

        self.assertEqual(self.client.get(reverse("devolver", args=[self.tripe.pk])).status_code, 200)
        devolucao = timezone.now() - timedelta(hours=1)
        self.client.post(reverse("devolver", args=[self.tripe.pk]), {"devolvido_em": data_hora(devolucao)})
        self.assertTrue(self.tripe.disponivel)
        uso.refresh_from_db()
        self.assertEqual(data_hora(uso.devolvido_em), data_hora(devolucao))
        self.assertEqual(uso.devolucao_registrada_por, self.admin)

    def test_solicitante_e_o_admin_logado(self):
        self.admin.first_name, self.admin.last_name = "Ana", "Lima"
        self.admin.save()
        self.client.force_login(self.admin)
        self.assertNotContains(self.client.get(reverse("pegar", args=[self.tripe.pk])), 'name="solicitante"')
        self.client.post(
            reverse("pegar", args=[self.tripe.pk]),
            {"solicitante": "Outra Pessoa", "retirado_por": self.matheus.pk, "retirado_em": data_hora(timezone.now()), "motivo": "y"},
        )
        self.assertEqual(self.tripe.uso_atual.solicitante, "Ana Lima")

    def test_entrega_exige_quem_pegou(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("pegar", args=[self.tripe.pk]),
            {"retirado_em": data_hora(timezone.now()), "motivo": "y"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.tripe.disponivel)

    def test_retirante_inativo_nao_aparece(self):
        self.matheus.ativo = False
        self.matheus.save()
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("pegar", args=[self.tripe.pk]))
        self.assertNotIn(self.matheus, resp.context["form"].fields["retirado_por"].queryset)

    def test_entrega_no_futuro_rejeitada(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("pegar", args=[self.tripe.pk]),
            {
                "retirado_por": self.matheus.pk,
                "retirado_em": data_hora(timezone.now() + timedelta(hours=2)),
                "motivo": "y",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.tripe.disponivel)

    def test_devolucao_antes_da_retirada_rejeitada(self):
        self.usar(self.matheus, retirado_em=timezone.now() - timedelta(hours=1))
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("devolver", args=[self.tripe.pk]),
            {"devolvido_em": data_hora(timezone.now() - timedelta(hours=2))},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.tripe.disponivel)

    def test_nao_entrega_objeto_em_uso(self):
        self.usar(self.sandro)
        self.client.force_login(self.admin)
        self.client.post(
            reverse("pegar", args=[self.tripe.pk]),
            {"retirado_por": self.matheus.pk, "retirado_em": data_hora(timezone.now()), "motivo": "y"},
        )
        self.assertEqual(Utilizacao.objects.filter(devolvido_em__isnull=True).count(), 1)
        self.assertEqual(self.tripe.uso_atual.retirado_por, self.sandro)

    def test_constraint_impede_dois_usos_abertos(self):
        from django.db import IntegrityError

        self.usar(self.sandro)
        with self.assertRaises(IntegrityError):
            self.usar(self.matheus)

    def test_historico_filtra_por_quem_pegou(self):
        self.usar(self.sandro, devolvido_em=timezone.now())
        self.usar(self.matheus)
        self.client.force_login(self.user)
        resp = self.client.get(reverse("historico"), {"retirante": self.matheus.pk})
        self.assertEqual([u.retirado_por for u in resp.context["pagina"]], [self.matheus])


class GestaoUsuariosTests(BaseTestCase):
    def test_utilizador_comum_sem_acesso(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("usuarios")).status_code, 302)
        self.assertEqual(self.client.get(reverse("usuario_criar")).status_code, 302)
        self.assertEqual(self.client.get("/admin/").status_code, 302)

    def test_admin_cadastra_admin_e_utilizador(self):
        self.client.force_login(self.admin)
        for login, is_staff in [("ana", True), ("pedro", False)]:
            dados = {
                "first_name": login.title(),
                "last_name": "Silva",
                "username": login,
                "email": "",
                "password1": "Cc0m-senha-segura",
                "password2": "Cc0m-senha-segura",
            }
            if is_staff:
                dados["is_staff"] = "on"
            resp = self.client.post(reverse("usuario_criar"), dados)
            self.assertRedirects(resp, reverse("usuarios"))
            self.assertEqual(User.objects.get(username=login).is_staff, is_staff)

    def test_admin_nao_remove_proprio_acesso(self):
        self.admin.first_name = "Chefe"
        self.admin.save()
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("usuario_editar", args=[self.admin.pk]),
            {"first_name": "Chefe", "username": "chefe", "is_active": "on"},
        )
        self.assertEqual(resp.status_code, 200)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff)
