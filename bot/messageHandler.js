const axios = require('axios');

async function handleMessage(msg) {
    const text = msg.body.trim();

    if (text.toLowerCase() === '!ajuda'){
        msg.reply(
            '🤖 *Comandos Disponiveis:*\n\n'+
            '*1. Angendar um Evento:*\n' +
            '`!agendar DD/MM/AAAA HH:MM Titulo do Evento`\n'+
            '_Exemplo: !agendar 25/12/2025 20:00 Ceia de Natal_'
        );
        return;
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