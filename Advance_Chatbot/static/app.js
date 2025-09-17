// --- DOM Elements ---
const chatContainer = document.getElementById('chat-container');
const promptForm = document.getElementById('prompt-form');
const promptInput = document.getElementById('prompt-input');
const sendButton = promptForm.querySelector('button[type="submit"]');
const micButton = document.getElementById('mic-button');
const attachButton = document.getElementById('attach-button');
const newChatButton = document.getElementById('new-chat-button');
const clearChatButton = document.getElementById('clear-chat-button');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const themeToggle = document.getElementById('theme-toggle');

// --- App State ---
let uploadedImage = null;
let isLoading = false;

// --- Utility Functions ---
function addCopyButton(messageElement) {
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-btn';
    copyButton.ariaLabel = 'Copy message';
    const copyIcon = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="currentColor"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>`;
    const checkIcon = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="currentColor"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>`;
    copyButton.innerHTML = copyIcon;

    copyButton.addEventListener('click', async () => {
        try {
            // Create a temporary element to parse the HTML and get the text
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = messageElement.innerHTML;
            // Remove the copy button from the temporary element before getting text
            const btn = tempDiv.querySelector('.copy-btn');
            if (btn) btn.remove();
            
            await navigator.clipboard.writeText(tempDiv.innerText);
            copyButton.innerHTML = checkIcon;
            setTimeout(() => {
                copyButton.innerHTML = copyIcon;
            }, 1500);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    });
    messageElement.appendChild(copyButton);
}

function createMessageElement(content, role) {
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // Convert markdown to HTML (simple implementation)
    content = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = content;
    messageWrapper.appendChild(messageDiv);
    return messageWrapper;
}

function createUserMessageElement(text, imageUrl) {
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    
    let content = '';
    if (imageUrl) {
        content += `<img src="${imageUrl}" alt="User upload" class="user-image-upload">`;
    }
    if (text) {
        content += text.replace(/\n/g, '<br>');
    }
    messageDiv.innerHTML = content;
    messageWrapper.appendChild(messageDiv);
    return messageWrapper;
}

function appendMessage(element) {
    chatContainer.appendChild(element);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function setFormState(loading) {
    isLoading = loading;
    promptInput.disabled = loading;
    sendButton.disabled = loading;
    micButton.disabled = loading;
    attachButton.disabled = loading;
}

function clearImagePreview() {
    uploadedImage = null;
    previewContainer.innerHTML = '';
    fileInput.value = ''; // Reset file input
}

// --- API Functions ---
async function sendMessage(message, image) {
    const data = { message };
    if (image) {
        data.image = image;
    }

    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to send message');
    }

    return await response.json();
}

async function clearChat() {
    const response = await fetch('/api/chat/clear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    });

    if (!response.ok) {
        throw new Error('Failed to clear chat');
    }

    return await response.json();
}

// --- Event Handlers ---
async function handleFormSubmit(event) {
    event.preventDefault();
    const prompt = promptInput.value.trim();
    const imageToSend = uploadedImage;

    if (!prompt && !imageToSend) {
        return;
    }

    setFormState(true);
    promptInput.value = '';
    clearImagePreview();

    const dataUrl = imageToSend ? `data:${imageToSend.mimeType};base64,${imageToSend.data}` : undefined;
    const userMessage = createUserMessageElement(prompt, dataUrl);
    appendMessage(userMessage);

    // Add loading indicator
    const loadingWrapper = document.createElement('div');
    loadingWrapper.className = 'message-wrapper';
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'message model loading-placeholder';
    loadingWrapper.appendChild(loadingIndicator);
    appendMessage(loadingWrapper);

    try {
        const response = await sendMessage(prompt, imageToSend);
        
        // Remove loading indicator
        loadingWrapper.remove();
        
        // Add AI response
        const responseWrapper = createMessageElement(response.response, 'model');
        
        // Add script indicator if detected
        if (response.detected_script && response.detected_script !== 'unknown') {
            const scriptIndicator = document.createElement('div');
            scriptIndicator.className = 'script-indicator';
            scriptIndicator.style.cssText = 'font-size: 0.75em; opacity: 0.6; margin-top: 5px; color: #8e6cc9; font-style: italic;';
            
            let scriptName = response.detected_script;
            if (scriptName === 'romanized_indic') scriptName = 'Romanized';
            else if (scriptName === 'romanized_hindi') scriptName = 'Romanized Hindi';
            else if (scriptName === 'romanized_marathi') scriptName = 'Romanized Marathi';
            else if (scriptName === 'devanagari') scriptName = 'देवनागरी';
            else if (scriptName === 'devanagari_hindi') scriptName = 'देवनागरी हिंदी';
            else if (scriptName === 'devanagari_marathi') scriptName = 'देवनागरी मराठी';
            else if (scriptName === 'latin') scriptName = 'Latin';
            
            scriptIndicator.textContent = `Script: ${scriptName}`;
            responseWrapper.querySelector('.message').appendChild(scriptIndicator);
        }
        
        // Add history length indicator if available
        if (response.history_length) {
            const historyIndicator = document.createElement('div');
            historyIndicator.className = 'history-indicator';
            historyIndicator.style.cssText = 'font-size: 0.7em; opacity: 0.5; margin-top: 3px; color: #666;';
            historyIndicator.textContent = `Context: ${response.history_length} messages`;
            responseWrapper.querySelector('.message').appendChild(historyIndicator);
        }
        
        appendMessage(responseWrapper);
        addCopyButton(responseWrapper.querySelector('.message'));

    } catch (error) {
        // Remove loading indicator
        loadingWrapper.remove();
        
        // Show error message
        const errorWrapper = createMessageElement(`**Error:** ${error.message}`, 'model');
        const errorMessage = errorWrapper.querySelector('.message');
        errorMessage.style.backgroundColor = '#d32f2f';
        appendMessage(errorWrapper);
    } finally {
        setFormState(false);
        promptInput.focus();
    }
}

function handleImageUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        const dataUrl = e.target.result;
        const [header, base64Data] = dataUrl.split(',');
        const mimeType = header.match(/:(.*?);/)?.[1] || 'application/octet-stream';

        uploadedImage = { data: base64Data, mimeType };

        // Create preview based on file type
        let previewContent = '';
        const fileName = file.name;
        const fileSize = (file.size / 1024 / 1024).toFixed(2) + ' MB';
        
        if (file.type.startsWith('image/')) {
            previewContent = `
                <div class="image-preview">
                    <img src="${dataUrl}" alt="Image preview" />
                    <div class="file-info">
                        <span class="file-name">${fileName}</span>
                        <span class="file-size">${fileSize}</span>
                    </div>
                    <button class="remove-image-btn" aria-label="Remove file">&times;</button>
                </div>
            `;
        } else if (file.type.startsWith('video/')) {
            previewContent = `
                <div class="image-preview file-preview">
                    <div class="file-icon">🎥</div>
                    <div class="file-info">
                        <span class="file-name">${fileName}</span>
                        <span class="file-size">${fileSize}</span>
                        <span class="file-type">Video</span>
                    </div>
                    <button class="remove-image-btn" aria-label="Remove file">&times;</button>
                </div>
            `;
        } else if (fileName.match(/\.(zip|rar|7z|tar|gz)$/i)) {
            previewContent = `
                <div class="image-preview file-preview">
                    <div class="file-icon">📦</div>
                    <div class="file-info">
                        <span class="file-name">${fileName}</span>
                        <span class="file-size">${fileSize}</span>
                        <span class="file-type">Archive</span>
                    </div>
                    <button class="remove-image-btn" aria-label="Remove file">&times;</button>
                </div>
            `;
        } else if (fileName.match(/\.(pdf|doc|docx|txt)$/i)) {
            previewContent = `
                <div class="image-preview file-preview">
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                        <span class="file-name">${fileName}</span>
                        <span class="file-size">${fileSize}</span>
                        <span class="file-type">Document</span>
                    </div>
                    <button class="remove-image-btn" aria-label="Remove file">&times;</button>
                </div>
            `;
        } else {
            previewContent = `
                <div class="image-preview file-preview">
                    <div class="file-icon">📁</div>
                    <div class="file-info">
                        <span class="file-name">${fileName}</span>
                        <span class="file-size">${fileSize}</span>
                        <span class="file-type">File</span>
                    </div>
                    <button class="remove-image-btn" aria-label="Remove file">&times;</button>
                </div>
            `;
        }
        
        previewContainer.innerHTML = previewContent;
        previewContainer
            .querySelector('.remove-image-btn')
            .addEventListener('click', clearImagePreview);
    };
    reader.readAsDataURL(file);
}

function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micButton.style.display = 'none';
        return;
    }

    const recognition = new SpeechRecognition();
    let isListening = false;
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
        isListening = true;
        micButton.classList.add('listening');
    };

    recognition.onend = () => {
        isListening = false;
        micButton.classList.remove('listening');
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        micButton.classList.remove('listening');
    };

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            transcript += event.results[i][0].transcript;
        }
        promptInput.value = transcript;
    };

    micButton.addEventListener('click', () => {
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
}

async function handleClearChat() {
    try {
        await clearChat();
        
        // Clear the visual chat container
        chatContainer.innerHTML = '';
        
        // Add welcome message back
        const welcomeWrapper = createMessageElement(
            "Hello! I'm Medicynth, your AI health assistant. How can I help you today?",
            'model'
        );
        appendMessage(welcomeWrapper);
        addCopyButton(welcomeWrapper.querySelector('.message'));
        
        clearImagePreview();
        promptInput.focus();
    } catch (error) {
        console.error('Error clearing chat:', error);
    }
}

function setupTheme() {
    const body = document.body;
    const savedTheme = localStorage.getItem('theme') || 'dark';
    body.dataset.theme = savedTheme;

    themeToggle.addEventListener('click', () => {
        const currentTheme = body.dataset.theme;
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        body.dataset.theme = newTheme;
        localStorage.setItem('theme', newTheme);
    });
}

// --- Initialize App ---
function initializeApp() {
    setupTheme();
    
    // Event listeners
    promptForm.addEventListener('submit', handleFormSubmit);
    attachButton.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleImageUpload);
    newChatButton.addEventListener('click', handleClearChat);
    clearChatButton.addEventListener('click', handleClearChat);
    
    // Setup speech recognition
    setupSpeechRecognition();
    
    // Add copy button to initial welcome message
    const initialMessage = chatContainer.querySelector('.message.model');
    if (initialMessage) {
        addCopyButton(initialMessage);
    }
    
    // Focus input
    promptInput.focus();
}

// Start the app
document.addEventListener('DOMContentLoaded', initializeApp);