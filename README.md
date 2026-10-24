# CCOM · Controle de Objetos

Sistema da Coordenação de Comunicação (CCOM) da Defensoria Pública de Roraima para controlar quem pegou cada equipamento, quando e por quê.

## Funcionalidades
- **Quadro público** (`/`): duas colunas.
  - *Não disponíveis*: objeto, quem está com ele, desde quando e o motivo.
  - *Disponíveis*: objeto, último utilizador, quando foi usado e o motivo.
  - A página se atualiza sozinha a cada minuto.
- **Pegar / Devolver**: o utilizador entra com o próprio login, clica em *Pegar* e informa o motivo. Só quem pegou (ou um administrador) pode devolver.
- **Histórico** (`/historico/`): todas as utilizações, com filtro por objeto e por usuário.
- **Usuários** (`/gestao/usuarios/`, só para administradores): cadastrar utilizadores e administradores, editar, trocar senha e desativar.
- **Admin** (`/admin/`): cadastrar, editar e desativar objetos e corrigir registros.

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
