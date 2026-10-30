# CCOM · Controle de Objetos

Sistema da Coordenação de Comunicação (CCOM) da Defensoria Pública de Roraima para controlar quem pegou cada equipamento, quando e por quê.

## Funcionalidades
- **Quadro público** (`/`): duas colunas.
  - *Não disponíveis*: objeto, quem está com ele, quem solicitou, desde quando e o motivo.
  - *Disponíveis*: objeto, último utilizador, quando foi usado e o motivo.
  - A página se atualiza sozinha a cada minuto.
- **Entrega / Devolução**: só administradores registram. Na entrega (*Pegar*), o administrador informa quem pegou o objeto (escolhido na lista de retirantes), o horário e o motivo; o solicitante é definido automaticamente como o administrador logado. Na devolução (*Devolver*), informa o horário. Os demais usuários só consultam o quadro e o histórico.
- **Retirantes**: lista de nomes que podem aparecer como "quem pegou" (inicialmente Celton, Luciana, Wallyson, Matheus, Ellainy, Sandro, Jeovana, Deboráh, Wesllyn, Valdir, Diego, Jair e Walber). Para incluir ou desativar nomes, use o Admin.
- **Login**: com *Manter conectado* marcado, a sessão dura 30 dias, renovados a cada acesso, mesmo com o computador desligado. Sem essa opção, ela termina ao fechar o navegador.
- **Histórico** (`/historico/`): todas as utilizações, com filtro por objeto e por quem pegou.
- **Usuários** (`/gestao/usuarios/`, só para administradores): cadastrar utilizadores e administradores, editar, trocar senha e desativar.
- **Admin** (`/admin/`): cadastrar, editar e desativar objetos e retirantes e corrigir registros.

Inventário (criado automaticamente pelas migrações, uma entrada por unidade, 55 no total): 3 câmeras Canon 5D Mark IV, 5 lentes, 7 baterias, 10 carregadores, 2 cartões de câmera, 2 filmadoras, 1 drone DJI Air 2S, 6 lapelas, 3 microfones Shure SV100, 4 LEDs, 8 tripés e suportes de celular, 1 estabilizador DJI 4SE e 3 cabos e adaptadores. Para incluir, editar ou desativar itens, use o Admin.

## Instalação
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # primeiro administrador
python manage.py runserver 0.0.0.0:8000
```
Depois, acesse `http://<ip-da-máquina>:8000/` na rede interna.

## Testes
```bash
python manage.py test objetos
```

## Produção
Defina as variáveis de ambiente `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` e `DJANGO_ALLOWED_HOSTS` (ex.: `ccom.intranet,10.0.0.5`), rode `python manage.py collectstatic` e sirva com gunicorn e nginx (ou outro servidor WSGI).
