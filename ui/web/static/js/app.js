// Main JavaScript for the Python Assistant Web UI

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const codeEditor = document.getElementById('code-editor');
    const runCodeButton = document.getElementById('run-code');
    const clearCodeButton = document.getElementById('clear-code');
    const codeOutput = document.getElementById('code-output');
    const clearOutputButton = document.getElementById('clear-output');
    const clearChatButton = document.getElementById('clear-chat');
    const themeToggleButton = document.getElementById('theme-toggle');
    
    // Initialize highlight.js
    hljs.highlightAll();
    
    // Check for saved theme preference
    if (localStorage.getItem('darkTheme') === 'true') {
        document.body.classList.add('dark-theme');
    }
    
    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    runCodeButton.addEventListener('click', executeCode);
    clearCodeButton.addEventListener('click', () => {
        codeEditor.value = '';
    });
    
    clearOutputButton.addEventListener('click', () => {
        codeOutput.innerHTML = '';
    });
    
    clearChatButton.addEventListener('click', clearChat);
    
    themeToggleButton.addEventListener('click', toggleTheme);
    
    // Auto-resize textarea
    userInput.addEventListener('input', autoResizeTextarea);
    
    // Functions
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        userInput.value = '';
        autoResizeTextarea();
        
        // Show loading indicator
        const loadingId = addLoadingMessage();
        
        // Send message to server
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            removeLoadingMessage(loadingId);
            
            // Add assistant message to chat
            addMessageToChat('assistant', data.response);
            
            // If there are code snippets, add them to the editor
            if (data.code_snippets && data.code_snippets.length > 0) {
                codeEditor.value = data.code_snippets[0];
            }
            
            // Scroll to bottom
            scrollToBottom();
            
            // Highlight code blocks
            highlightCodeBlocks();
        })
        .catch(error => {
            // Remove loading indicator
            removeLoadingMessage(loadingId);
            
            // Show error message
            addMessageToChat('system', 'Error: Failed to get response. Please try again.');
            console.error('Error:', error);
        });
    }
    
    function executeCode() {
        const code = codeEditor.value.trim();
        if (!code) return;
        
        // Clear previous output
        codeOutput.innerHTML = '<div class="output-running">Running code...</div>';
        
        // Send code to server for execution
        fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        })
        .then(response => response.json())
        .then(data => {
            // Clear output
            codeOutput.innerHTML = '';
            
            // Display output
            if (data.output) {
                const outputElement = document.createElement('div');
                outputElement.textContent = data.output;
                codeOutput.appendChild(outputElement);
            }
            
            // Display error
            if (data.error) {
                const errorElement = document.createElement('div');
                errorElement.className = 'output-error';
                errorElement.textContent = data.error;
                codeOutput.appendChild(errorElement);
            }
            
            // Display success message
            if (data.success && !data.error) {
                const successElement = document.createElement('div');
                successElement.className = 'output-success';
                successElement.textContent = 'Code executed successfully!';
                codeOutput.appendChild(successElement);
                
                // If code was saved, show the path
                if (data.saved_path) {
                    const savedElement = document.createElement('div');
                    savedElement.textContent = `Code saved to: ${data.saved_path}`;
                    codeOutput.appendChild(savedElement);
                }
            }
        })
        .catch(error => {
            codeOutput.innerHTML = `<div class="output-error">Error: Failed to execute code. ${error.message}</div>`;
            console.error('Error:', error);
        });
    }
    
    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process content for code blocks
        const formattedContent = formatMessageContent(content);
        contentDiv.innerHTML = formattedContent;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        scrollToBottom();
    }
    
    function formatMessageContent(content) {
        // Replace code blocks with properly formatted HTML
        let formattedContent = content.replace(/```python([\s\S]*?)```/g, function(match, code) {
            return `<pre><code class="language-python">${escapeHtml(code.trim())}</code></pre>`;
        });
        
        // Replace regular code blocks
        formattedContent = formattedContent.replace(/```([\s\S]*?)```/g, function(match, code) {
            return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
        });
        
        // Replace inline code
        formattedContent = formattedContent.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Replace newlines with <br> tags outside of code blocks
        formattedContent = formattedContent.replace(/\n(?![^<]*<\/code>)/g, '<br>');
        
        return formattedContent;
    }
    
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    function addLoadingMessage() {
        const id = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message system';
        loadingDiv.id = id;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<p>Thinking...</p>';
        
        loadingDiv.appendChild(contentDiv);
        chatMessages.appendChild(loadingDiv);
        
        scrollToBottom();
        
        return id;
    }
    
    function removeLoadingMessage(id) {
        const loadingDiv = document.getElementById(id);
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function highlightCodeBlocks() {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
    
    function clearChat() {
        // Clear chat UI
        chatMessages.innerHTML = `
            <div class="message system">
                <div class="message-content">
                    <p>Chat history cleared. How can I help you with Python today?</p>
                </div>
            </div>
        `;
        
        // Clear chat history on server
        fetch('/api/clear', {
            method: 'POST'
        })
        .catch(error => {
            console.error('Error clearing chat history:', error);
        });
    }
    
    function toggleTheme() {
        document.body.classList.toggle('dark-theme');
        localStorage.setItem('darkTheme', document.body.classList.contains('dark-theme'));
    }
    
    function autoResizeTextarea() {
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    }
    
    // Load chat history on page load
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                // Clear default welcome message
                chatMessages.innerHTML = '';
                
                // Add messages to chat
                data.messages.forEach(msg => {
                    addMessageToChat(msg.role, msg.content);
                });
                
                // Highlight code blocks
                highlightCodeBlocks();
            }
        })
        .catch(error => {
            console.error('Error loading chat history:', error);
        });
});
