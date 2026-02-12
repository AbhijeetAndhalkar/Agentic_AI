document.addEventListener('DOMContentLoaded', () => {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');
    const closeChatBtn = document.getElementById('close-chat');
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const messagesContainer = document.getElementById('messages-container');

    // Toggle Chat
    function toggleChat() {
        if (chatWindow.classList.contains('chat-closed')) {
            chatWindow.classList.remove('chat-closed');
            chatWindow.classList.add('chat-open');
            userInput.focus();
        } else {
            chatWindow.classList.add('chat-closed');
            chatWindow.classList.remove('chat-open');
        }
    }

    if (chatToggleBtn) chatToggleBtn.addEventListener('click', toggleChat);
    if (closeChatBtn) closeChatBtn.addEventListener('click', toggleChat);

    // Send Message
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add User Message
        appendMessage('user', message);
        userInput.value = '';

        // Add Loading Indicator
        const loadingId = appendLoading();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();

            // Remove Loading and Add Bot Response
            removeLoading(loadingId);
            appendMessage('bot', data.response || "Sorry, I encountered an error.");
        } catch (error) {
            console.error('Error:', error);
            removeLoading(loadingId);
            appendMessage('bot', "Sorry, I'm having connection issues.");
        }
    }

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (userInput) userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} w-full`;

        const content = document.createElement('div');
        // Updated classes for new theme
        content.className = sender === 'user'
            ? 'user-message message-bubble shadow-sm'
            : 'bot-message message-bubble shadow-sm border border-white/50';
        content.textContent = text;

        div.appendChild(content);
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function appendLoading() {
        const id = 'loading-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'flex justify-start w-full';
        div.innerHTML = `
            <div class="bot-message message-bubble shadow-sm border border-white/50">
                <div class="flex space-x-1">
                    <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                    <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
