document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');

    // Conversation history to send to backend
    let conversationHistory = [];

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = userInput.value.trim();
        if (!msg) return;

        // 1. Add user message to UI
        addMessage(msg, 'user-message');
        conversationHistory.push({ role: 'user', content: msg });
        
        // 2. Clear input
        userInput.value = '';
        
        // 3. Show typing indicator and scroll to bottom
        typingIndicator.style.display = 'flex';
        scrollToBottom();

        // 4. Send to backend API
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: conversationHistory })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch response');
            }

            const data = await response.json();
            
            // 5. Hide typing indicator
            typingIndicator.style.display = 'none';

            // 6. Add bot response to UI and history
            const botMsg = data.response;
            addMessage(botMsg, 'bot-message', true);
            conversationHistory.push({ role: 'assistant', content: botMsg });

        } catch (error) {
            console.error('Chat error:', error);
            typingIndicator.style.display = 'none';
            addMessage(`Sorry, I encountered an error: ${error.message}. Please check your API key and connection.`, 'bot-message');
        }
    });

    function addMessage(text, className, isMarkdown = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isMarkdown && typeof marked !== 'undefined') {
            contentDiv.innerHTML = marked.parse(text);
        } else {
            contentDiv.textContent = text;
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
