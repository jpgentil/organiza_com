# CCOM · Controle de Objetos

Sistema da Coordenação de Comunicação (CCOM) da Defensoria Pública de Roraima para controlar quem pegou cada equipamento, quando e por quê.

## Funcionalidades
- **Quadro público** (`/`): duas colunas.
  - *Não disponíveis*: objeto, quem está com ele, quem solicitou, desde quando e o motivo.
  - *Disponíveis*: objeto, último utilizador, quando foi usado e o motivo.
  - A página se atualiza sozinha a cada minuto.
- **Entrega / Devolução**: só administradores registram. Na entrega (*Pegar*), o administrador informa o solicitante, quem pegou o objeto (escolhido na lista de retirantes), o horário e o motivo. Na devolução (*Devolver*), informa o horário. Os demais usuários só consultam o quadro e o histórico.
- **Retirantes**: lista de nomes que podem aparecer como "quem pegou" (inicialmente Celton, Luciana, Wallyson, Matheus, Ellainy, Sandro, Jeovana, Deboráh e Wesllyn). Para incluir ou desativar nomes, use o Admin.
- **Histórico** (`/historico/`): todas as utilizações, com filtro por objeto e por quem pegou.
- **Usuários** (`/gestao/usuarios/`, só para administradores): cadastrar utilizadores e administradores, editar, trocar senha e desativar.
- **Admin** (`/admin/`): cadastrar, editar e desativar objetos e retirantes e corrigir registros.

Inventário inicial (criado automaticamente): 1 lapela, 3 kits de câmera, 1 drone, 6 tripés e 2 filmadoras.

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
