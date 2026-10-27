from django.db import migrations, models

INVENTARIO = [
    ("camera", "Câmera Canon 5D Mark IV", 3),
    ("lente", "Lente 24-70mm", 2),
    ("lente", "Lente 50mm", 2),
    ("lente", "Lente 70-200mm", 1),
    ("bateria", "Bateria de câmera", 4),
    ("bateria", "Bateria de câmera LP-E17", 2),
    ("bateria", "Bateria de LED NP-F960", 1),
    ("carregador", "Carregador de bateria duplo", 3),
    ("carregador", "Carregador de bateria LC-E17E", 2),
    ("carregador", "Carregador de bateria NP-F960", 1),
    ("carregador", "Carregador de pilhas", 4),
    ("cartao", "Cartão de câmera", 2),
    ("filmadora", "Filmadora", 2),
    ("drone", "Drone DJI Air 2S", 1),
    ("lapela", "Lapela", 1),
    ("lapela", "Lapela BOYA", 3),
    ("lapela", "Lapela K9", 2),
    ("microfone", "Microfone Shure SV100", 3),
    ("iluminacao", "LED grande U800+", 2),
    ("iluminacao", "LED YN160 III", 2),
    ("tripe", "Tripé de celular com suporte", 5),
    ("tripe", "Tripé flexível MTG-023", 2),
    ("tripe", "Suporte para celular BMG-40", 1),
    ("estabilizador", "Estabilizador de celular DJI 4SE", 1),
    ("acessorio", "Cabo P2-P2", 2),
    ("acessorio", "Adaptador iPhone/P2 HS-16", 1),
]

# Itens do inventário inicial que continuam existindo com outro nome
# (mantém o histórico de uso).
RENOMEADOS = {
    "Kit de câmera 1": "Câmera Canon 5D Mark IV 1",
    "Kit de câmera 2": "Câmera Canon 5D Mark IV 2",
    "Kit de câmera 3": "Câmera Canon 5D Mark IV 3",
    "Drone": "Drone DJI Air 2S",
}

# Itens do inventário inicial que não estão na lista nova.
FORA_DA_LISTA = [f"Tripé {i}" for i in range(1, 7)]


def nomes():
    for categoria, rotulo, quantidade in INVENTARIO:
        if quantidade == 1:
            yield categoria, rotulo
        else:
            for i in range(1, quantidade + 1):
                yield categoria, f"{rotulo} {i}"


def atualizar(apps, schema_editor):
    Objeto = apps.get_model("objetos", "Objeto")
    for antigo, novo in RENOMEADOS.items():
        if not Objeto.objects.filter(nome=novo).exists():
            Objeto.objects.filter(nome=antigo).update(nome=novo)

    for categoria, nome in nomes():
        Objeto.objects.update_or_create(nome=nome, defaults={"categoria": categoria, "ativo": True})

    # Um tripé emprestado agora continua no quadro até ser devolvido;
    # depois disso, desative-o pelo Admin.
    Utilizacao = apps.get_model("objetos", "Utilizacao")
    em_uso = Utilizacao.objects.filter(devolvido_em__isnull=True).values("objeto_id")
    Objeto.objects.filter(nome__in=FORA_DA_LISTA).exclude(pk__in=em_uso).update(ativo=False)


def reverter(apps, schema_editor):
    Objeto = apps.get_model("objetos", "Objeto")
    Objeto.objects.filter(nome__in=FORA_DA_LISTA).update(ativo=True)
    for antigo, novo in RENOMEADOS.items():
        Objeto.objects.filter(nome=novo).update(nome=antigo, categoria="kit_camera" if "Kit" in antigo else "drone")
    Objeto.objects.filter(nome__in=[nome for _, nome in nomes()], utilizacoes__isnull=True).exclude(
        nome__in=["Lapela", "Filmadora 1", "Filmadora 2"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("objetos", "0004_retirantes_iniciais")]

    operations = [
        migrations.AlterField(
            model_name="objeto",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("camera", "Câmera"),
                    ("lente", "Lente"),
                    ("bateria", "Bateria"),
                    ("carregador", "Carregador"),
                    ("cartao", "Cartão de memória"),
                    ("filmadora", "Filmadora"),
                    ("drone", "Drone"),
                    ("lapela", "Lapela"),
                    ("microfone", "Microfone"),
                    ("iluminacao", "Iluminação"),
                    ("tripe", "Tripé e suporte"),
                    ("estabilizador", "Estabilizador"),
                    ("acessorio", "Acessório e cabo"),
                    ("outro", "Outro"),
                ],
                default="outro",
                max_length=20,
                verbose_name="categoria",
            ),
        ),
        migrations.RunPython(atualizar, reverter),
    ]
