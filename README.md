# 🎮 GameTracker v2

Sistema completo de organização de games com IA, PWA nativo, modo claro/escuro, RAWG API e exportação.

---

## 🚀 Setup rápido (6 comandos)

```cmd
cd gametracker2
pip install -r requirements.txt
python manage.py makemigrations games
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Acesse: **http://localhost:8000**

---

## 👤 Conta de teste (já populada)

| Campo   | Valor             |
|---------|-------------------|
| Usuário | `jogador`         |
| Senha   | `gametracker123`  |

10 jogos já cadastrados: Elden Ring, RDR2, Last of Us, God of War, Hollow Knight, Cyberpunk 2077, Stardew Valley, Hades, Zelda BotW e Baldur's Gate 3.

---

## 🔑 Configurar APIs

Edite `gametracker/settings.py`:

```python
RAWG_API_KEY  = 'sua_chave'   # https://rawg.io/apidocs (gratuito)
GROQ_API_KEY  = 'sua_chave'   # https://console.groq.com (gratuito)
```

---

## 📱 Instalar como app no celular

**Android (Chrome):**
1. Abra `http://SEU_IP:8000` no Chrome
2. Menu (⋮) → **"Adicionar à tela inicial"**
3. Confirme — abre sem barra de endereço!

**iOS (Safari):**
1. Abra no Safari
2. Botão compartilhar → **"Adicionar à Tela de Início"**

Para acessar da rede local:
```cmd
python manage.py runserver 0.0.0.0:8000
```
Descubra seu IP: `ipconfig` → campo "Endereço IPv4"

---

## 🌗 Modo claro / escuro

Toggle no canto superior direito da navbar. Preferência salva automaticamente no navegador. Detecta automaticamente o tema do sistema na primeira visita.

---

## ✨ Funcionalidades v2

| Feature | Descrição |
|---|---|
| 🌗 Tema claro/escuro | Toggle + persistência + detecção automática do sistema |
| 📱 PWA nativo | Standalone, sem barra de endereço, ícones gerados |
| 🔍 RAWG autocomplete | Busca em tempo real com capa e metadados |
| 🤖 IA (Groq/OpenAI) | Insights personalizados por jogo |
| 📊 Dashboard | Gráficos adaptativos ao tema |
| 🎮 Nav mobile | Bottom navigation + botão central de adição |
| 👤 Conta demo | 10 jogos pré-cadastrados para teste |
| 📤 Export | CSV (Excel) + PDF |
| 🏷️ Tags | Sistema de categorização colorido |
| ⭐ Avaliação | Nota 0-10 + review + stars |

---

## 🗂️ Estrutura

```
gametracker2/
├── gametracker/        # Config Django
├── games/              # App principal
│   ├── models.py       # Game, Platform, Tag
│   ├── views.py        # CRUD, dashboard, AI, export
│   ├── services.py     # RAWG + Groq/OpenAI
│   └── management/commands/seed_data.py
├── templates/          # HTML com modo claro/escuro
├── static/
│   ├── icons/          # icon-192.png, icon-512.png
│   ├── manifest.json   # PWA manifest
│   └── sw.js           # Service Worker
└── requirements.txt
```

---

## 🔧 Rodar no celular (rede local)

```cmd
python manage.py runserver 0.0.0.0:8000
```

Acesse do celular: `http://192.168.x.x:8000`

---

## ⚡ Criar superusuário (admin)

```cmd
python manage.py createsuperuser
```

Admin: **http://localhost:8000/admin**
