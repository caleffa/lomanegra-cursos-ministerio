'use strict';

// Set client auth mode - true to enable client auth, false to disable it
const isClientAuthEnabled = true;

/**
 * Function to generate JWT tokens. It returns a Promise to provide tokens.
 * The function is passed to SDK which uses it to fetch token whenever it needs
 * to establish a connection to the chat server. If a user ID isn't passed in, 
 * as in this function, then the token server generates one.
 * @returns {Promise} Promise to provide a signed JWT token
 */
var generateToken = function (sessionId) {
    console.log(sessionId);
    return new Promise((resolve) => {
        fetch('/api/chatbotciudadanos/token').then((
                response) => {
                console.log(sessionId);
                console.log(response);
                if (response.status !== 200) {
                    console.log(
                        'Hubo un problema con el chatbot. Status Code: ${response.status}.');
                    return;
                }

                // Examine the text in the response
                response.json().then(function (data) {
                    resolve(data.token);
                });
            })
    });
}

/**
 * Initializes the SDK and sets a global field with passed name for which
 * it can be referred to later.
 *
 * @param {string} name Name by which the chat widget should be referred
 */
const initSdk = (name) => {
    if (!name) {
        name = 'Bots';          // Set default reference name to 'Bots'
    }
    let Bots;

    setTimeout(() => {

        /**
            * SDK configuration settings
            * Other than URI, all fields are optional with two exceptions for auth modes
            * In client auth disabled mode, 'channelId' must be passed, 'userId' is optional
            * In client auth enabled mode, 'clientAuthEnabled: true' must be passed
            */
        let chatWidgetSettings = {
            URI: 'oda-814bde67457c4fce8f3a9c661fc50b95-da10.data.digitalassistant.oci.oraclecloud.com',
            openChatOnLoad: false,
            clientAuthEnabled: isClientAuthEnabled,            
            timestampFormat: 'HH:mm',
            enableAttachment: false,            
            initUserHiddenMessage: 'Hola!',            
            showConnectionStatus: true,
            conversationBeginPosition: 'bottom',            
            position: { bottom: '2px', right: '2px' },
            // botButtonIcon: 'images/chatbot/bot-button.png',
            logoIcon: 'favicon.ico',
            botIcon: 'favicon.ico',
            personIcon: 'images/chatbot/user-icon.png', 
            font: '12px Verdana, Geneva, sans-serif',            
            // theme: 'classic',
            i18n: {
                en: {
                    chatTitle: 'Portal Empleo',
                    connected: 'en linea',
                    connecting: 'Conectando...',
                    disconnected: 'Desconectado',
                    closing : 'Desconectando...',
                    inputPlaceholder: 'Escribe un mensaje',
                    send: 'Enviar (Enter)',
                    audioResponseOff: 'Habilitar audio',
                    audioResponseOn: 'Deshabilitar audio',
                    close: 'Cerrar'
                }
            },
            enableBotAudioResponse: true,
            height: '80vh',
            width: '25vw'
        };

        // Initialize SDK
        if (isClientAuthEnabled) {
            Bots = new WebSDK(chatWidgetSettings, generateToken);
        } else {
            Bots = new WebSDK(chatWidgetSettings);
        }

        // Connect to the ODA
        Bots.connect();

        // Create global object to refer Bots
        window[name] = Bots;
    }, 0);
};
