'use client';

import { useState } from 'react';
import DependencyGraph from '@/components/DependencyGraph';
import CodeEditor from '@/components/CodeEditor';
import ChatInterface from '@/components/ChatInterface';
import TimelineSlider from '@/components/TimelineSlider';

export default function Home() {
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [repoUrl, setRepoUrl] = useState('https://github.com/example/repo');
  const [faultType, setFaultType] = useState('race_condition');

  const startMission = async (repoUrl: string, faultType: string) => {
    setIsLoading(true);
    try {
      // Mock mode - simulate backend response
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSessionId('demo-session-' + Date.now());
    } catch (error) {
      console.error('Failed to start mission:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white">
      <header className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">ChronoGraph</h1>
          {!sessionId && (
            <div className="flex gap-2 items-center">
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="GitHub repo URL"
                className="bg-gray-700 rounded px-3 py-2 w-64"
              />
              <select
                value={faultType}
                onChange={(e) => setFaultType(e.target.value)}
                className="bg-gray-700 rounded px-3 py-2"
              >
                <option value="race_condition">Race Condition</option>
                <option value="memory_leak">Memory Leak</option>
                <option value="deadlock">Deadlock</option>
              </select>
              <button
                onClick={() => startMission(repoUrl, faultType)}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded disabled:opacity-50"
              >
                {isLoading ? 'Starting...' : 'Start Mission'}
              </button>
            </div>
          )}
          {sessionId && (
            <span className="text-green-400 text-sm">Session: {sessionId}</span>
          )}
        </div>
      </header>
      
      <div className="flex-1 grid grid-cols-2 gap-4 p-4">
        <div className="flex flex-col gap-4">
          <DependencyGraph sessionId={sessionId} />
          <TimelineSlider />
        </div>
        
        <div className="flex flex-col gap-4">
          <CodeEditor />
          <ChatInterface sessionId={sessionId} />
        </div>
      </div>
    </div>
  );
}
