'use client';

import { useState } from 'react';

interface ChatInterfaceProps {
  sessionId: string;
}

export default function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // Mock tutor response
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const mockResponses = [
      "Let's use the Scaffolding approach. First, what do you observe about the handle_request() function?",
      "Good observation! Now, what programming concept might be relevant when multiple threads access shared resources?",
      "Exactly! What could you try to ensure thread-safe access to the database?",
      "Notice that handle_request() calls db_save() without any synchronization. What happens when two threads call this simultaneously?"
    ];
    
    const response = mockResponses[messages.length % mockResponses.length];
    setMessages(prev => [...prev, { role: 'assistant', content: response }]);
  };

  return (
    <div className="flex flex-col h-96 bg-gray-800 rounded-lg border border-gray-700">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`${msg.role === 'user' ? 'text-blue-400' : 'text-green-400'}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>
      
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about the bug..."
            className="flex-1 bg-gray-700 rounded px-3 py-2 outline-none"
          />
          <button
            onClick={sendMessage}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
