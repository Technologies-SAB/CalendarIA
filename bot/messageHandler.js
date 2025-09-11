const axios = require('axios');

const userEventLists = {};
const userStates = {};

async function handleMessage(msg) {
    const text = msg.body.trim();
    const userChatId = msg.from;
    const currentUserState = userStates[userChatId];

    if (currentUserState && currentUserState.command === 'agendar') {
        await handleAgendaStep(msg, currentUserState);
        return; 
    }

    if (text.toLowerCase() === '!ajuda') {
        return msg.reply(
            '🤖 *Comandos Disponíveis:*\n\n' +
            '*1. Agendar:* `!agendar` (inicia a conversa)\n\n' +
            '*2. Listar:* `!proximos` (eventos dos próximos 7 dias)\n\n' +
            '*3. Ver Detalhes:* `!ver <id>` (use o ID da lista)\n\n' +
            '*4. Apagar:* `!apagar <id>` (apaga de ambos os calendários)\n\n' +
            '*5. Cancelar:* `!cancelar` (interrompe o agendamento)'
        );
    }

    if (text.toLowerCase() === '!proximos') {
        try {
            await msg.reply('🔎 Buscando seus próximos 7 dias de compromissos...');
            const response = await axios.get(`${process.env.CALENDAR_URL}/proximos`);
            const eventos = response.data;

            if (!eventos || eventos.length === 0) {
                delete userEventLists[userChatId];
                return msg.reply('🎉 Você não tem nenhum evento futuro na sua agenda para os próximos 7 dias.');
            }

            userEventLists[userChatId] = eventos;

            let resposta = '🗓️ *Seus próximos compromissos:*\n(Use `!ver <id>` para mais detalhes)\n\n';
            eventos.forEach((evento, index) => {
                const id_amigavel = index + 1;
                const dataEvento = new Date(evento.inicio);
                const dataFormatada = dataEvento.toLocaleString('pt-BR', {
                    weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                });
                resposta += `*${id_amigavel}.* ${dataFormatada} - ${evento.titulo}\n`;
            });

            return msg.reply(resposta);
        } catch (error) {
            console.error('Erro ao buscar eventos:', error.response?.data || error.message);
            return msg.reply('❌ Ocorreu um erro ao buscar seus eventos.');
        }
    }

    if (text.startsWith('!ver ')) {
        const id_amigavel = parseInt(text.substring(5).trim(), 10);
        const userEvents = userEventLists[userChatId];

        if (!userEvents) {
            return msg.reply('Você precisa usar o comando `!proximos` primeiro para depois ver os detalhes de um evento.');
        }
        if (isNaN(id_amigavel) || id_amigavel < 1 || id_amigavel > userEvents.length) {
            return msg.reply(`❌ ID inválido. Por favor, escolha um número entre 1 e ${userEvents.length}.`);
        }

        const evento = userEvents[id_amigavel - 1];

        const inicio = new Date(evento.inicio).toLocaleString('pt-BR');
        const fimProvisorio = new Date(new Date(evento.inicio).getTime() + 60*60*1000).toLocaleString('pt-BR');


        let resposta = `*Detalhes do Evento:*\n\n`
        resposta += `*Título:* ${evento.titulo}\n`;
        resposta += `*Início:* ${inicio}\n`;
        resposta += `*Fim:* ${evento.fim}\n`;
        resposta += `*Origem:* ${evento.origem}\n\n`;
        resposta += `_ID Real:_ \`${evento.id}\``;

        return msg.reply(resposta);
    }

    if (text.startsWith('!apagar ')) {
        try {
            const id_amigavel = parseInt(text.substring(8).trim(), 10);
            const userEvents = userEventLists[userChatId];
            
            if (!userEvents) {
                return msg.reply('Você precisa usar o comando `!proximos` primeiro para depois apagar um evento.');
            }
        
            if (isNaN(id_amigavel) || id_amigavel < 1 || id_amigavel > userEvents.length) {
                return msg.reply(`❌ ID inválido. Por favor, escolha um número entre 1 e ${userEvents.length}.`);
            }

            const eventoParaApagar = userEvents[id_amigavel - 1];

            await msg.reply(`🗑️ Tentando apagar o evento *"${eventoParaApagar.titulo}"* de ambos os calendários...`);

            const response = await axios.delete(`${process.env.CALENDAR_URL}/apagar`, {
                data: { 
                    id: eventoParaApagar.id,
                    origem: eventoParaApagar.origem,
                    titulo: eventoParaApagar.titulo,
                    inicio: eventoParaApagar.inicio
                }
            });

            const { google, apple } = response.data;
            let resposta = "📊 *Relatório da Operação:*\n\n";
            resposta += `*Google Calendar:* ${google.message}\n`;
            resposta += `*iCloud Calendar:* ${apple.message}`;

            return msg.reply(resposta);

        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Ocorreu um erro desconhecido ao tentar apagar.';
            console.error('Erro ao apagar evento:', errorMessage);
            return msg.reply(`❌ ${errorMessage}`);
        }
    }

    if (text.startsWith('!agendar')) {

        userStates[userChatId] = {
            command: 'agendar',
            step: 1,
            eventData: {}
        };
        await msg.reply('Ok, vamos agendar um novo evento! ✨\n\n*Qual será o título do evento?*\n\n(Digite `!cancelar` a qualquer momento para parar.)');
        return;
    }
    
    if (text.toLowerCase() === '!cancelar') {
        if (userStates[userChatId]) {
            delete userStates[userChatId];
            await msg.reply('Operação cancelada. 👍');
        } else {
            await msg.reply('Não há nenhuma operação em andamento para cancelar.');
        }
        return;
    }
}

async function handleAgendaStep(msg, state) {
    const text = msg.body.trim();
    const userChatId = msg.from;

    if (text.toLowerCase() === '!cancelar') {
        delete userStates[userChatId];
        await msg.reply('Agendamento cancelado. 👍');
        return;
    }

    switch (state.step) {
        case 1:
            state.eventData.title = text;
            state.step = 2;
            await msg.reply('*Qual a data do evento?* (formato DD/MM/AAAA)');
            break;

        case 2:
            if (!/^\d{2}\/\d{2}\/\d{4}$/.test(text)) {
                await msg.reply('❌ Formato de data inválido. Por favor, use DD/MM/AAAA.');
                return;
            }
            state.eventData.date = text;
            state.step = 3;
            await msg.reply('*Qual o horário de início?* (formato HH:MM)');
            break;

        case 3:
             if (!/^\d{2}:\d{2}$/.test(text)) {
                await msg.reply('❌ Formato de hora inválido. Por favor, use HH:MM.');
                return;
            }
            state.eventData.hour = text;
            state.step = 4;
            await msg.reply('*Adicione uma descrição* (ou digite "nenhuma").');
            break;

        case 4:
            state.eventData.description = (text.toLowerCase() === 'nenhuma') ? '' : text;
            
            await msg.reply(`Ok, confirmando...\n` +
                `*Título:* ${state.eventData.title}\n` +
                `*Data:* ${state.eventData.date}\n` +
                `*Hora:* ${state.eventData.hour}\n\n` +
                `⏳ Agendando...`);

            try {
                await axios.post(`${process.env.CALENDAR_URL}/agendar`, state.eventData);
                await msg.reply('✅ Evento agendado com sucesso em ambos os calendários!');
            } catch (error) {
                console.error('Erro ao agendar evento conversacional:', error.response?.data || error.message);
                await msg.reply('❌ Ocorreu um erro no servidor ao tentar agendar.');
            } finally {
                delete userStates[userChatId];
            }
            break;
    }
}

module.exports = { handleMessage }