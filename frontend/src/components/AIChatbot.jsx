import React, { useState, useRef, useEffect } from 'react';
import { Paperclip, X, AlertCircle } from 'lucide-react';
import './AIChatbot.css';

function AIChatbot({ userId, context }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file type (PDF, images, text)
      const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'text/plain'];
      if (!validTypes.includes(file.type)) {
        alert('Please upload PDF, image (JPG/PNG), or text files only');
        return;
      }
      
      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }

      setAttachedFile(file);
    }
  };

  const removeAttachment = () => {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const sendMessage = async () => {
    if (!input.trim() && !attachedFile) return;

    let messageContent = input;
    
    // If file is attached, convert to base64 and include in message
    if (attachedFile) {
      messageContent += `\n\n[Attached: ${attachedFile.name}]`;
      
      // For demo, we'll just mention the file
      // In production, you'd upload to storage and send URL
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64 = reader.result.split(',')[1];
        await sendToAPI(messageContent, { 
          fileName: attachedFile.name, 
          fileType: attachedFile.type,
          fileData: base64.substring(0, 1000) // Send just preview for demo
        });
      };
      reader.readAsDataURL(attachedFile);
      removeAttachment();
    } else {
      await sendToAPI(messageContent);
    }
  };

  const sendToAPI = async (messageText, fileData = null) => {
    const userMessage = { role: 'user', content: messageText };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const payload = {
        user_id: userId,
        message: messageText,
        context: context
      };

      if (fileData) {
        payload.attached_file = fileData;
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const aiMessage = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '❌ Sorry, I encountered an error. Please check if the backend is running and try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearHistory = async () => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/chat/clear/${userId}`, {
        method: 'POST'
      });
      setMessages([]);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button 
        className="chat-toggle-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chat"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-header-content">
              <h3>🤖 ORBIT Assistant</h3>
              <p className="chat-subtitle">Ask me anything about opportunities</p>
            </div>
            <div className="chat-header-actions">
              <button onClick={clearHistory} className="clear-btn" title="Clear history">
                🗑️
              </button>
              <button onClick={() => setIsOpen(false)} className="close-btn">
                ✕
              </button>
            </div>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-welcome">
                <p className="welcome-title">👋 Hi! I'm your ORBIT assistant.</p>
                <p className="welcome-subtitle">Ask me about:</p>
                <ul className="welcome-list">
                  <li>📋 Eligibility requirements</li>
                  <li>📈 Profile improvements</li>
                  <li>💡 Application tips</li>
                  <li>🎯 Opportunity details</li>
                  <li>📎 Share competition PDFs/images</li>
                  <li>🔗 Check if links are safe to visit</li>
                </ul>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content" style={{ whiteSpace: 'pre-wrap' }}>
                  {msg.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            {attachedFile && (
              <div className="attachment-preview">
                <Paperclip className="icon-xs" />
                <span>{attachedFile.name}</span>
                <button onClick={removeAttachment} className="remove-attachment">
                  <X className="icon-xs" />
                </button>
              </div>
            )}
            
            <div className="input-row">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.webp,.txt"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="attach-btn"
                title="Attach file (PDF, image, text)"
                disabled={loading}
              >
                <Paperclip className="icon-sm" />
              </button>
              
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything or attach a competition poster..."
                rows="2"
                disabled={loading}
              />
              
              <button 
                onClick={sendMessage} 
                disabled={loading || (!input.trim() && !attachedFile)}
                className="send-btn"
              >
                {loading ? '⏳' : '➤'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AIChatbot;
