const { Client, LocalAuth } = require('whatsapp-web.js');
const { handleMessage } = require('./messageHandler.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--single-process',
      '--disable-gpu'
    ],
  }
});

function initialize() {
    console.log('Iniciando o cliente WhatsApp...');

    client.on('qr', qr => {
        console.log('--------------------------------------------------');
        console.log('ESCANEAR O QR CODE ABAIXO COM SEU WHATSAPP');
        console.log('Vá em Aparelhos Conectados > Conectar um aparelho');
        console.log('--------------------------------------------------');
        qrcode.generate(qr, { small: true }); 
    
        console.log('Se o QR Code não aparecer direito, copie a string abaixo e use um gerador online.');
        console.log('QR CODE TEXTO:', qr);
    });

    client.on('ready', () => {
        console.log('==================================================');
        console.log('✅ Bot WhatsApp pronto e conectado!');
        console.log('==================================================');
    });

    client.on('message', handleMessage);

    client.initialize();
}

module.exports = { initialize }