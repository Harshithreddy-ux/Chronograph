'use client';

import { useState } from 'react';
import DependencyGraph from '@/components/DependencyGraph';
import CodeEditor from '@/components/CodeEditor';
import ChatInterface from '@/components/ChatInterface';
import TimelineSlider from '@/components/TimelineSlider';

export default function Home() {
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCode, setSelectedCode] = useState('# Select a function from the graph to view code');
  const [selectedFunction, setSelectedFunction] = useState<string>('');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://35.172.115.54:8000/api/upload/code', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setSessionId(data.session_id);
      alert('Code uploaded and analyzed! Session: ' + data.session_id);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Make sure backend is running on port 8000.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeClick = async (nodeData: any) => {
    if (nodeData.type === 'Function') {
      // Fetch function source code
      try {
        const response = await fetch(`http://35.172.115.54:8000/api/function/${nodeData.name}?file=${nodeData.file_path}`);
        const data = await response.json();
        setSelectedCode(data.source || '# Code not available');
        setSelectedFunction(nodeData.name);
      } catch (error) {
        console.error('Failed to fetch function code:', error);
        setSelectedCode(`# Function: ${nodeData.name}\n# Error loading code`);
        setSelectedFunction(nodeData.name);
      }
    } else {
      setSelectedCode(`# File: ${nodeData.path || nodeData.name}\n# Click on a function to view its code`);
      setSelectedFunction('');
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white">
      <header className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">ChronoGraph - AI Debugging Tutor</h1>
          {!sessionId && (
            <label className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded cursor-pointer">
              {isLoading ? 'Uploading...' : 'Upload Python Code'}
              <input 
                type="file" 
                accept=".py" 
                onChange={handleFileUpload}
                className="hidden"
                disabled={isLoading}
              />
            </label>
          )}
          {sessionId && (
            <div className="flex gap-4 items-center">
              <span className="text-green-400 text-sm">Session: {sessionId}</span>
              <button
                onClick={() => setSessionId('')}
                className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded text-sm"
              >
                Upload New File
              </button>
            </div>
          )}
        </div>
      </header>
      
      <div className="flex-1 grid grid-cols-2 gap-4 p-4">
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="text-lg font-semibold mb-2">Dependency Graph</h2>
            <DependencyGraph sessionId={sessionId} onNodeClick={handleNodeClick} />
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">Execution Timeline</h2>
            <TimelineSlider />
          </div>
        </div>
        
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="text-lg font-semibold mb-2">Code View</h2>
            <CodeEditor code={selectedCode} selectedFunction={selectedFunction} />
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">AI Tutor</h2>
            <ChatInterface sessionId={sessionId} />
          </div>
        </div>
      </div>
    </div>
  );
}
