document.addEventListener('DOMContentLoaded', () => {
    // === DOM Element Selections ===
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const connectButton = document.getElementById('connect-button');
    const connectionStatus = document.getElementById('connection-status');
    
    // === Application State ===
    let isConnected = false;
    let chat_history = [];

    // === Core Functions ===

    /**
     * Appends a new message to the chat history.
     * @param {string} sender - The sender of the message ('user' or 'assistant').
     * @param {string} message - The text content of the message.
     */
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chatHistory.appendChild(messageElement);
        // Automatically scroll to the bottom of the chat
        chatHistory.scrollTop = chatHistory.scrollHeight;

        // Update local chat history
        chat_history.push({ sender, message });
    }

    /**
     * Handles sending a message.
     */
    async function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;
        
        if (!isConnected) {
            appendMessage('assistant', 'Please connect to the database first.');
            return;
        }

        appendMessage('user', userMessage);
        userInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage, history: chat_history }),
            });

            const data = await response.json();
            if (data.status === 'success') {
                appendMessage('assistant', data.message);
            } else {
                appendMessage('assistant', `Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            appendMessage('assistant', 'Sorry, something went wrong with the connection.');
        }
    }

    /**
     * Handles the database connection logic.
     */
    async function connectToDatabase() {
        connectionStatus.textContent = 'Connecting...';
        connectButton.disabled = true;

        try {
            const response = await fetch('/connect', {
                method: 'POST',
            });

            const data = await response.json();
            if (data.status === 'success') {
                isConnected = true;
                connectionStatus.textContent = 'Connected!';
                connectButton.style.backgroundColor = '#4CAF50';
                connectButton.textContent = 'Connected';
                // Display initial message
                appendMessage('assistant', "Hello! I'm a SQL assistant. Ask me anything about your database.");
            } else {
                isConnected = false;
                connectionStatus.textContent = `Connection failed: ${data.message}`;
                connectButton.disabled = false;
            }
        } catch (error) {
            isConnected = false;
            connectionStatus.textContent = 'Connection failed.';
            connectButton.disabled = false;
        }
    }

    // === Event Listeners ===
    sendButton.addEventListener('click', sendMessage);
    connectButton.addEventListener('click', connectToDatabase);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});