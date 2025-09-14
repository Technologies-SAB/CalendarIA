const axios = require('axios');

const userStates = {};
const userEventLists = {}; 

async function handleMessage(msg) {
    const texto = msg.body.trim();
    const userChatId = msg.from;

    const currentUserState = userStates[userChatId];
    if (currentUserState && currentUserState.command === 'agendar') {
        await handleAgendaStep(msg, currentUserState);
        return; 
    }

    const command = texto.toLowerCase().split(' ')[0];

    switch (command) {
        case '!ajuda':
            await msg.reply(
                '🤖 *Comandos Disponíveis:*\n\n' +
                '*1. Conectar Conta:*\n`!conectar <google|outlook|apple>`\n_Ex: !conectar google_\n\n' +
                '*2. Agendar Evento:*\n`!agendar` (inicia a conversa)\n\n' +
                '*3. Listar Próximos Eventos:*\n`!proximos` (próximos 7 dias)\n\n' +
                '*4. Ver Detalhes de um Evento:*\n`!ver <id>` (use o ID da lista)\n\n' +
                '*5. Apagar um Evento:*\n`!apagar <id>` (apaga de todos os calendários)\n\n' +
                '*6. Cancelar Ação:*\n`!cancelar` (interrompe o agendamento)'
            );
            break;
        
        case '!conectar':
            const provider = texto.split(' ')[1];
            const baseUrl = process.env.API_BASE_URL || 'http://localhost:8000';
            let authUrl;

            if (provider === 'google') {
                authUrl = `${baseUrl}/auth/google/login?chat_id=${userChatId}`;
                await msg.reply(`Clique no link para conectar seu Google Calendar:\n\n${authUrl}`);
            } else if (provider === 'outlook') {
                authUrl = `${baseUrl}/outlook/start-auth?chat_id=${userChatId}`;
                await msg.reply(`Clique no link para conectar seu Outlook:\n\n${authUrl}`);
            } else if (provider === 'apple') {
                await msg.reply('Para conectar sua conta Apple (iCloud), preciso do seu email e de uma senha específica de aplicativo.\n\n' +
                                'Use o comando no seguinte formato:\n`!conectar apple seu-email@icloud.com sua-senha-de-app`\n\n' +
                                '⚠️ *Atenção:* Use uma senha gerada em appleid.apple.com, nunca sua senha principal.');
            } else {
                await msg.reply('Provedor desconhecido. Use `!conectar <google|outlook|apple>`.');
            }
            break;

        case '!agendar':
            userStates[userChatId] = { command: 'agendar', step: 1, eventData: {} };
            await msg.reply('Qual o título do evento?\n\n(Digite `!cancelar` a qualquer momento)');
            break;

        case '!cancelar':
            await msg.reply('Não há nenhuma operação em andamento para cancelar.');
            break;
            
        case '!proximos':
            try {
                await msg.reply('🔎 Buscando seus próximos 7 dias de compromissos...');
                const response = await axios.post(`${process.env.CALENDAR_URL}/proximos`, { chat_id: userChatId });
                const eventos = response.data;
                
                if (!eventos || eventos.length === 0) {
                    delete userEventLists[userChatId];
                    return msg.reply('🎉 Você não tem nenhum evento futuro na sua agenda.');
                }

                userEventLists[userChatId] = eventos;
                let resposta = '🗓️ *Seus próximos compromissos:*\n(Use `!ver <id>` ou `!apagar <id>`)\n\n';
                eventos.forEach((evento, index) => {
                    const id_amigavel = index + 1;
                    const dataEvento = new Date(evento.inicio);
                    const dataFormatada = dataEvento.toLocaleString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
                    resposta += `*${id_amigavel}.* [${evento.origem}] ${dataFormatada} - ${evento.titulo}\n`;
                });
                await msg.reply(resposta);
            } catch (error) {
                await msg.reply(`❌ Erro ao buscar eventos: ${error.response?.data?.detail || error.message}`);
            }
            break;
        
        case '!ver':
            try {

                const id_amigavel_str = texto.split(' ')[1];
                if (!id_amigavel_str) {
                    return msg.reply('Você precisa informar o ID do evento. Ex: `!ver 1`');
                }
                const id_amigavel = parseInt(id_amigavel_str, 10);

                const userEvents = userEventLists[userChatId];

                if (!userEvents) {
                    return msg.reply('Você precisa usar o comando `!proximos` primeiro para depois ver os detalhes de um evento.');
                }
                if (isNaN(id_amigavel) || id_amigavel < 1 || id_amigavel > userEvents.length) {
                    return msg.reply(`❌ ID inválido. Por favor, escolha um número entre 1 e ${userEvents.length}.`);
                }

                const evento = userEvents[id_amigavel - 1];

                const inicio = new Date(evento.inicio).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

                const fimProvisorio = new Date(new Date(evento.inicio).getTime() + 60 * 60 * 1000).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

                let resposta = `*Detalhes do Evento ID ${id_amigavel}:*\n\n`;
                resposta += `*Título:* ${evento.titulo}\n`;
                resposta += `*Início:* ${inicio}\n`;
                resposta += `*Fim (Estimado):* ${fimProvisorio}\n`; // Usa a variável correta
                resposta += `*Origem:* ${evento.origem.charAt(0).toUpperCase() + evento.origem.slice(1)}\n\n`;
                resposta += `_ID Real (para debug):_ \`${evento.id}\``;

                return msg.reply(resposta);
            } catch (error) {
                console.error("Erro no comando !ver:", error);
                return msg.reply("Ocorreu um erro ao buscar os detalhes do evento.");
            }
            break;

        case '!apagar':
            try {
                const id_amigavel = parseInt(texto.split(' ')[1], 10);
                const userEvents = userEventLists[userChatId];
                
                if (!userEvents) {
                    return msg.reply('Você precisa usar `!proximos` primeiro para depois apagar um evento.');
                }
                if (isNaN(id_amigavel) || id_amigavel < 1 || id_amigavel > userEvents.length) {
                    return msg.reply(`❌ ID inválido. Escolha um número entre 1 e ${userEvents.length}.`);
                }

                const eventoParaApagar = userEvents[id_amigavel - 1];
                await msg.reply(`🗑️ Tentando apagar *"${eventoParaApagar.titulo}"* de todos os calendários...`);

                const response = await axios.delete(`${process.env.CALENDAR_URL}/apagar`, {
                    data: { 
                        chat_id: userChatId,
                        titulo: eventoParaApagar.titulo,
                        inicio: eventoParaApagar.inicio
                    }
                });

                const resultados = response.data.resultados;
                let resposta = "📊 *Relatório da Operação:*\n\n";
                resultados.forEach(res => {
                    const provider = res.provider.charAt(0).toUpperCase() + res.provider.slice(1);
                    resposta += `*${provider}:* ${res.message}\n`;
                });
                await msg.reply(resposta);
            } catch (error) {
                await msg.reply(`❌ Erro ao apagar: ${error.response?.data?.detail || error.message}`);
            }
            break;
    }
}

async function handleAgendaStep(msg, state) {
    const texto = msg.body.trim();
    const userChatId = msg.from;

    if (texto.toLowerCase() === '!cancelar') {
        delete userStates[userChatId];
        await msg.reply('Agendamento cancelado.');
        return;
    }

    switch (state.step) {

        case 1:
            state.eventData.titulo = texto;
            state.step = 2;
            await msg.reply('Qual a data? (DD/MM/AAAA)');
            break;

        case 2:
            state.eventData.data = texto;
            state.step = 3;
            await msg.reply('Qual a hora? (HH:MM)');
            break;

        case 3:
            state.eventData.hora = texto;
            state.step = 4;
            await msg.reply('Alguma descrição? (ou digite "nenhuma")');
            break;

        case 4:
            state.eventData.description = (texto.toLowerCase() === 'nenhuma') ? '' : texto;
            await msg.reply(`⏳ Agendando em todos os seus calendários...`);
            
            try {
                const payload = { chat_id: userChatId, ...state.eventData };
                const response = await axios.post(`${process.env.CALENDAR_URL}/agendar`, payload);
                
                const resultados = response.data.resultados;
                let resposta = '✅ *Relatório de Agendamento:*\n\n';
                resultados.forEach(res => {
                    const provider = res.provider.charAt(0).toUpperCase() + res.provider.slice(1);
                    resposta += `*${provider}:* ${res.message}\n`;
                });
                await msg.reply(resposta);

            } catch (error) {
            
                await msg.reply(`❌ Erro ao agendar: ${error.response?.data?.detail || error.message}`);
            
            } finally {
            
                delete userStates[userChatId];
            
            }
            
            break;
    }
}

module.exports = { handleMessage };