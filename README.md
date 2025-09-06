# 📆 CalendarIA 🤖 - Integração do WhatsApp com Apple Calendar e Google Calendar!

Estruturado Projeto pensada até o momento:
```
📂 projeto-bot/
│
├── bot/                      # Serviço Node.js (WhatsApp Bot)
│   ├── index.js              # Entrada principal do bot                              ██████████ 100%
│   ├── whatsapp.js           # Conexão com WhatsApp (whatsapp-web.js ou Meta API)    ██████████ 100%
│   ├── routes.js             # Rotas para comunicação com o microserviço Python      ██████████ 100%
│   ├── package.json                                                                  ██████████ 100%
|   ├── Dockerfile            # Arquivo para buildar o service em Node.js             ██████████ 100%
│   └── .env
│
├── calendar-service/         # Serviço Python (Google + Apple Calendar)
│   ├── main.py               # FastAPI/Flask para expor rotas REST                   ██████████ 100%
|   ├── google/
│       ├── google_calendar.py    # Integração com Google Calendar                    ██████████ 100%
|   ├── apple/
│       ├── apple_calendar.py     # Integração com Apple Calendar (CalDAV/pyicloud)   ██████████ 100%
│   ├── requirements.txt                                                              ██████████ 100%
|   ├── Dockerfile            # Arquivo para buildar o service em Python              ██████████ 100%
│   └── .env                                                                          ██████████ 100%
│
└── docker-compose.yml        # Orquestração dos serviços
```


