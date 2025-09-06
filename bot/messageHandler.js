const axios = require('axios');

async function handleMessage(msg) {
    const text = msg.body.trim();

    if (text.toLowerCase() === '!ajuda'){
        msg.reply(
            '🤖 *Comandos Disponiveis:*\n\n'+
            '*1. Angendar um Evento:*\n' +
            '`!agendar DD/MM/AAAA HH:MM Titulo do Evento`\n'+
            '_Exemplo: !agendar 25/12/2025 20:00 Ceia de Natal_\n\n\n'+
            '*1. Proximos eventos:*\n'+
            '!proximos - Mostra os eventos dos proximos 7 dias a partir da data atual.'
        );
        return;
    }

    if (texto.toLowerCase() === '!proximos') {
        try {
            await msg.reply('🔎 Buscando seus próximos 7 dias de compromissos...');
            const response = await axios.get(`${process.env.CALENDAR_URL}/proximos`);
            const eventos = response.data;

            if (!eventos || eventos.length === 0) {
                return msg.reply('🎉 Você não tem nenhum evento futuro na sua agenda para os próximos 7 dias.');
            }

            let resposta = '🗓️ *Seus próximos compromissos:*\n\n';
            eventos.forEach(evento => {
                const dataEvento = new Date(evento.inicio);
                const dataFormatada = dataEvento.toLocaleString('pt-BR', {
                    weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                });
                resposta += `*${dataFormatada}* - ${evento.titulo}\n`;
            });

            return msg.reply(resposta);

        } catch (error) {
            console.error('Erro ao buscar eventos:', error.response?.data || error.message);
            return msg.reply('❌ Ocorreu um erro ao buscar seus eventos.');
        }
    }

    if (text.startsWith('!agendar ')) {
        const args = text.substring(9).trim();
        const parts = args.split(' ');

        if (parts.length < 3){
            msg.reply('❌ Formato incorreto!\n\n Use `!agendar DD/MM/AAAA HH:MM Titulo do Evento`');
            return
        }

        const date = parts[0];
        const hour = parts[1];
        const title = parts.slice(2).join(' ');
        const description = ' olá';

        if (!/^\d{2}\/\d{2}\/\d{4}$/.test(date) || !/^\d{2}:\d{2}$/.test(hour)) {
            msg.reply('❌ Data ou hora em formato incorreto!\n\n Use `DD/MM/AAAA` e `HH:MM`.');
            return
        }

        try {
            await msg.reply(`⏳ Agendando... "${title}"`);
            
            await axios.post(`${process.env.CALENDAR_URL}/agendar`, {
                date, hour, title, description
            });

            await msg.reply(`✅ Evento agendado com sucesso: *${title}* em *${date} às ${hour}*`);
        } catch (error) {
            console.error('Erro ao chamar a API de calendário:', error.response?.data || error.message);
            await msg.reply('❌ Ocorreu um erro no servidor ao tentar agendar. Verifique os logs da API.');
        }
    }
}

module.exports = { handleMessage }