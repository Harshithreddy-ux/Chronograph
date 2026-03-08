'use client';

import { useState, useEffect, useRef } from 'react';

interface ChatInterfaceProps {
  sessionId: string;
  selectedCode?: string;
  selectedFunction?: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `http://${window.location.hostname}:8000` : 'http://localhost:8000');

export default function ChatInterface({ sessionId, selectedCode, selectedFunction }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '👋 **Welcome to ChronoGraph!**\n\nUpload your Python code and I\'ll help you understand it. You can:\n\n• Click any **function** in the graph to see its code\n• Ask me questions about specific functions\n• Get explanations of bugs and patterns\n\nLet\'s get started!'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (sessionId) {
      setMessages([{
        role: 'assistant',
        content: '🚀 **Code uploaded successfully!**\n\nI can now help you with:\n\n• **Explaining** what functions do\n• **Finding** potential bugs\n• **Understanding** code relationships\n\nClick a function in the graph and ask me about it!'
      }]);
    }
  }, [sessionId]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    if (!sessionId) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '⚠️ Please upload code first before asking questions.' 
      }]);
      return;
    }

    // Add code context if available
    let messageWithContext = input;
    if (selectedCode && selectedFunction && !selectedCode.startsWith('#')) {
      messageWithContext = `Analyzing function: ${selectedFunction}\n\nCode:\n${selectedCode}\n\nQuestion: ${input}`;
    }

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageWithContext,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '❌ Error connecting to AI backend. Make sure the server is running on port 8000 and Neo4j is accessible.' 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full min-h-0">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg ${
              msg.role === 'user' 
                ? 'bg-gradient-to-br from-cyan-400 to-blue-600' 
                : 'bg-gradient-to-br from-purple-500 to-pink-500'
            }`}>
              <i className={`fas fa-${msg.role === 'user' ? 'user-circle' : 'robot'} text-white text-lg`}></i>
            </div>
            <div className={`bg-gray-700/50 backdrop-blur-sm rounded-2xl px-4 py-3 max-w-[75%] ${
              msg.role === 'user' ? 'rounded-tr-none' : 'rounded-tl-none'
            }`}>
              <div 
                className="text-sm text-gray-200 leading-relaxed prose prose-invert prose-sm max-w-none"
                dangerouslySetInnerHTML={{ 
                  __html: msg.content
                    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-bold text-white">$1</strong>')
                    .replace(/\*(.+?)\*/g, '<em class="italic text-gray-300">$1</em>')
                    .replace(/`(.+?)`/g, '<code class="bg-gray-800 px-1.5 py-0.5 rounded text-cyan-400 font-mono text-xs">$1</code>')
                    .replace(/^### (.+)$/gm, '<h3 class="text-base font-bold text-white mt-3 mb-2">$1</h3>')
                    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-bold text-white mt-4 mb-2">$1</h2>')
                    .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold text-white mt-4 mb-3">$1</h1>')
                    .replace(/^• (.+)$/gm, '<li class="ml-4 mb-1">$1</li>')
                    .replace(/\n\n/g, '<br/><br/>')
                    .replace(/\n/g, '<br/>')
                }}
              />
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
              <i className="fas fa-robot text-white text-lg"></i>
            </div>
            <div className="bg-gray-700/50 backdrop-blur-sm rounded-2xl rounded-tl-none px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t border-gray-700 bg-gray-800/30">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about the bug..."
            disabled={!sessionId}
            className="flex-1 bg-gray-700/50 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={!sessionId || !input.trim()}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-xl text-white font-medium transition flex items-center gap-2 shadow-lg hover:shadow-xl"
          >
            <i className="fas fa-paper-plane"></i>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
