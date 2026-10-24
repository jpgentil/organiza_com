from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Objeto, Utilizacao


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123", first_name="Maria")
        self.outro = User.objects.create_user("joao", password="senha-forte-123", first_name="João")
        self.admin = User.objects.create_user("chefe", password="senha-forte-123", is_staff=True)
        self.tripe = Objeto.objects.get(nome="Tripé 1")


class InventarioTests(TestCase):
    def test_inventario_inicial(self):
        self.assertEqual(Objeto.objects.count(), 13)
        self.assertEqual(Objeto.objects.filter(categoria="tripe").count(), 6)
        self.assertEqual(Objeto.objects.filter(categoria="kit_camera").count(), 3)
        self.assertEqual(Objeto.objects.filter(categoria="filmadora").count(), 2)
        self.assertTrue(Objeto.objects.filter(nome="Lapela").exists())
        self.assertTrue(Objeto.objects.filter(nome="Drone").exists())


class QuadroTests(BaseTestCase):
    def test_quadro_publico_sem_botoes(self):
        resp = self.client.get(reverse("quadro"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["disponiveis"]), 13)
        self.assertNotContains(resp, "Pegar</a>")

    def test_quadro_mostra_quem_esta_com_objeto(self):
        Utilizacao.objects.create(objeto=self.tripe, usuario=self.user, motivo="Evento no auditório")
        resp = self.client.get(reverse("quadro"))
        self.assertEqual([o.nome for o in resp.context["indisponiveis"]], ["Tripé 1"])
        self.assertContains(resp, "Maria")
        self.assertContains(resp, "Evento no auditório")


class PegarDevolverTests(BaseTestCase):
    def test_pegar_exige_login(self):
        resp = self.client.get(reverse("pegar", args=[self.tripe.pk]))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('pegar', args=[self.tripe.pk])}")

    def test_pegar_e_devolver(self):
        self.client.force_login(self.user)
        self.client.post(reverse("pegar", args=[self.tripe.pk]), {"motivo": "Gravação"})
        self.assertFalse(self.tripe.disponivel)

        self.client.post(reverse("devolver", args=[self.tripe.pk]))
        self.assertTrue(self.tripe.disponivel)
        ultimo = self.tripe.ultimo_uso
        self.assertEqual((ultimo.usuario, ultimo.motivo), (self.user, "Gravação"))

    def test_nao_pega_objeto_em_uso(self):
        Utilizacao.objects.create(objeto=self.tripe, usuario=self.outro, motivo="x")
        self.client.force_login(self.user)
        self.client.post(reverse("pegar", args=[self.tripe.pk]), {"motivo": "y"})
        self.assertEqual(Utilizacao.objects.filter(devolvido_em__isnull=True).count(), 1)
        self.assertEqual(self.tripe.uso_atual.usuario, self.outro)

    def test_constraint_impede_dois_usos_abertos(self):
        from django.db import IntegrityError

        Utilizacao.objects.create(objeto=self.tripe, usuario=self.outro, motivo="x")
        with self.assertRaises(IntegrityError):
            Utilizacao.objects.create(objeto=self.tripe, usuario=self.user, motivo="y")

    def test_outro_usuario_nao_devolve(self):
        Utilizacao.objects.create(objeto=self.tripe, usuario=self.outro, motivo="x")
        self.client.force_login(self.user)
        self.client.post(reverse("devolver", args=[self.tripe.pk]))
        self.assertFalse(self.tripe.disponivel)

    def test_admin_devolve_por_outro(self):
        Utilizacao.objects.create(objeto=self.tripe, usuario=self.outro, motivo="x")
        self.client.force_login(self.admin)
        self.client.post(reverse("devolver", args=[self.tripe.pk]))
        self.assertTrue(self.tripe.disponivel)


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
