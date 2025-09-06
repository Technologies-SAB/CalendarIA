# 📆 CalendarIA 🤖 - Integração do WhatsApp com Apple Calendar e Google Calendar!

Estruturado Projeto pensada até o momento:
```
📂 projeto-bot/
│
├── bot/                      # Serviço Node.js (WhatsApp Bot)
│   ├── index.js              # Entrada principal do bot
│   ├── whatsapp.js           # Conexão com WhatsApp (whatsapp-web.js ou Meta API)
│   ├── routes.js             # Rotas para comunicação com o microserviço Python
│   ├── package.json
│   └── .env
│
├── calendar-service/         # Serviço Python (Google + Apple Calendar)
│   ├── main.py               # FastAPI/Flask para expor rotas REST
│   ├── google_calendar.py    # Integração com Google Calendar
│   ├── apple_calendar.py     # Integração com Apple Calendar (CalDAV/pyicloud)
│   ├── requirements.txt
│   └── .env
│
└── docker-compose.yml        # Orquestração dos serviços
```


