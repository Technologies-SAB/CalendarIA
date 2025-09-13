# 📆 CalendarIA 🤖 - Integração do WhatsApp com Apple Calendar e Google Calendar!

Estruturado Projeto pensada até o momento:
```
📂 projeto-bot/
│
├── database/                 # Serviço de Banco de Dados
│   └── Dockerfile
│
├── bot/                      # Serviço Node.js (WhatsApp Bot)
│   ├── index.js                  # Entrada principal do bot                               ██████████ 100%
│   ├── whatsapp.js               # Conexão com WhatsApp (whatsapp-web.js ou Meta API)     ██████████ 100%
│   ├── routes.js                 # Rotas para comunicação com o microserviço Python       ██████████ 100%
│   ├── package.json                                                                       ██████████ 100%
|   ├── Dockerfile                # Arquivo para buildar o service em Node.js              ██████████ 100%
│   └── .env
│
├── calendar_service/             # Serviço Python
│   ├── main.py                   # FastAPI/Flask para expor rotas REST                    ██████████ 100%
|   ├── crud.py                   # Funções para interagir com o DB                        ██████████ 100%
|   ├── database.py               # Configuração da conexão com o DB                       ██████████ 100%
│   ├── models.py                 # Define a estrutura das tabelas do DB                   ██████████ 100%
│   └── auth/                     # Lógica para o fluxo de OAuth de cada serviço           ██████████ 100%
│       ├── google_auth.py
|
│   └── providers/                # Novo: Lógica específica de cada calendário
│       ├── google_provider.py
│       ├── apple_provider.py
│        
|   └── google/
│       ├── google_calendar.py    # Integração com Google Calendar                         ██████████ 100%
|   └── apple/
│       ├── apple_calendar.py     # Integração com Apple Calendar (CalDAV/pyicloud)        ██████████ 100%
│   ├── requirements.txt                                                                   ██████████ 100%
|   ├── Dockerfile                # Arquivo para buildar o service em Python               ██████████ 100%
│   └── .env                                                                               ██████████ 100%
│
├── calendar_service_dotnet/      # Serviço .Net/C#
│   ├── Controllers/              # Pontos de entrada da API (ex: AuthController, CalendarController)
│   ├── Services/                 # Lógica de negócios (ex: OutlookCalendarService)
│   ├── appsettings.json          # Arquivo de configuração com Client ID/Secret
│   └── Program.cs                # Configuração da aplicação
|
└── docker-compose.yml        # Orquestração dos serviços
```


