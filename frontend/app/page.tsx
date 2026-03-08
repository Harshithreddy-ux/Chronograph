'use client';

import { useState, useEffect } from 'react';
import DependencyGraph from '@/components/DependencyGraph';
import CodeEditor from '@/components/CodeEditor';
import ChatInterface from '@/components/ChatInterface';
import TimelineSlider from '@/components/TimelineSlider';

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `http://${window.location.hostname}:8000` : 'http://localhost:8000');

export default function Home() {
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCode, setSelectedCode] = useState('# Select a function from the graph to view code');
  const [selectedFunction, setSelectedFunction] = useState<string>('');
  const [sessionTime, setSessionTime] = useState('00:00');
  const [funcCount, setFuncCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);
  const [improvementCount, setImprovementCount] = useState(0);
  const [graphKey, setGraphKey] = useState(0); // Force graph refresh

  useEffect(() => {
    if (sessionId) {
      const startTime = Date.now();
      const interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const secs = (elapsed % 60).toString().padStart(2, '0');
        setSessionTime(`${mins}:${secs}`);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [sessionId]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsLoading(true);

    try {
      // Upload each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_URL}/api/upload/code`, {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        
        // Only set session ID on first file
        if (i === 0) {
          setSessionId(data.session_id);
        }
        
        // Update counts (accumulate from all files)
        setFuncCount(prev => prev + (data.graph?.nodes?.filter((n: any) => n.type === 'Function').length || 0));
        setErrorCount(prev => prev + (data.errors || 0));
        setImprovementCount(prev => prev + (data.improvements || 0));
      }
      
      // Force graph refresh after all uploads
      setGraphKey(prev => prev + 1);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Make sure backend is running.');
    } finally {
      setIsLoading(false);
      // Reset file input
      e.target.value = '';
    }
  };

  const handleClearSession = async () => {
    if (confirm('Clear current session and start fresh?')) {
      // Clear Neo4j graph
      try {
        await fetch(`${API_URL}/api/graph/clear`, { method: 'POST' });
      } catch (error) {
        console.error('Clear error:', error);
      }
      
      // Reset all state
      setSessionId('');
      setSelectedCode('# Select a function from the graph to view code');
      setSelectedFunction('');
      setSessionTime('00:00');
      setFuncCount(0);
      setErrorCount(0);
      setImprovementCount(0);
      setGraphKey(prev => prev + 1); // Force graph to refresh
    }
  };

  const handleNodeClick = async (nodeData: any) => {
    if (nodeData.type === 'Function') {
      try {
        const response = await fetch(`${API_URL}/api/function/${nodeData.name}?file=${nodeData.file_path}`);
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 text-white flex flex-col">
      {/* Animated Background Particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-96 h-96 bg-purple-500/10 rounded-full blur-3xl -top-48 -left-48 animate-pulse"></div>
        <div className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl -bottom-48 -right-48 animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 flex flex-col h-screen">
        {/* Header */}
        <header className="bg-gradient-to-r from-purple-600 via-blue-600 to-purple-600 bg-[length:200%_100%] animate-gradient p-6 shadow-2xl flex-shrink-0">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center shadow-lg">
                <i className="fas fa-code text-white text-2xl"></i>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">ChronoGraph</h1>
                <p className="text-purple-100 text-sm">Agentic Code Learning Platform</p>
              </div>
            </div>
            
            {!sessionId ? (
              <label className="relative cursor-pointer group">
                <div className="bg-white text-purple-600 font-semibold px-6 py-3 rounded-lg flex items-center gap-2 shadow-lg hover:shadow-xl transition-all hover:scale-105">
                  <i className="fas fa-rocket"></i>
                  {isLoading ? 'Uploading...' : sessionId ? 'Add More Files' : 'Upload Python Code'}
                </div>
                <input 
                  type="file" 
                  accept=".py" 
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={isLoading}
                  multiple
                />
              </label>
            ) : (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 bg-green-500/20 backdrop-blur-sm border border-green-500/30 px-4 py-2 rounded-lg">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-green-100 text-sm font-medium">Active Session</span>
                </div>
                <button
                  onClick={handleClearSession}
                  className="bg-red-500/20 hover:bg-red-500/30 backdrop-blur-sm border border-red-500/30 px-4 py-2 rounded-lg text-sm transition flex items-center gap-2 text-red-200 hover:text-red-100"
                >
                  <i className="fas fa-trash-alt"></i>
                  Clear
                </button>
                <button
                  onClick={() => setSessionId('')}
                  className="bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 px-4 py-2 rounded-lg text-sm transition"
                >
                  New Upload
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Main Content - Scrollable */}
        <div className="flex-1 overflow-auto">
          <div className="grid grid-cols-2 gap-6 p-6 max-w-7xl mx-auto w-full">
            {/* Left Column */}
            <div className="flex flex-col gap-6">
              {/* Dependency Graph */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/50 overflow-hidden shadow-xl hover:shadow-2xl transition-shadow flex flex-col h-[500px]">
                <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-700/50 flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center">
                    <i className="fas fa-project-diagram text-white"></i>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Dependency Graph</h3>
                    <p className="text-gray-400 text-xs">Interactive code visualization</p>
                  </div>
                </div>
                <div className="flex-1 min-h-0">
                  <DependencyGraph key={graphKey} sessionId={sessionId} onNodeClick={handleNodeClick} />
                </div>
              </div>

              {/* Timeline */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/50 p-6 shadow-xl">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                    <i className="fas fa-history text-white"></i>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Time Travel Debugger</h3>
                    <p className="text-gray-400 text-xs">Navigate execution timeline</p>
                  </div>
                </div>
                <TimelineSlider sessionId={sessionId} />
              </div>
            </div>

            {/* Right Column */}
            <div className="flex flex-col gap-6">
              {/* Code Editor */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/50 overflow-hidden shadow-xl h-[280px]">
                <div className="bg-gradient-to-r from-gray-700/50 to-gray-800/50 px-4 py-3 flex items-center justify-between border-b border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                      <i className="fas fa-code text-white text-sm"></i>
                    </div>
                    <span className="text-sm font-semibold text-white">Code Editor</span>
                  </div>
                  <div className="flex gap-1">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                </div>
                <CodeEditor code={selectedCode} selectedFunction={selectedFunction} />
              </div>

              {/* Chat Interface */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/50 overflow-hidden shadow-xl flex flex-col h-[500px]">
                <div className="bg-gradient-to-r from-blue-600/50 to-purple-600/50 px-4 py-3 flex items-center justify-between border-b border-gray-700 flex-shrink-0">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                      <i className="fas fa-robot text-blue-600 text-sm"></i>
                    </div>
                    <div>
                      <span className="text-sm font-semibold text-white">AI Tutor</span>
                      <div className="flex items-center gap-2 text-xs text-blue-100">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span>Online</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex-1 min-h-0">
                  <ChatInterface 
                    sessionId={sessionId} 
                    selectedCode={selectedCode}
                    selectedFunction={selectedFunction}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Stats */}
        <div className="bg-gray-800/30 backdrop-blur-sm border-t border-gray-700 px-6 py-4 flex-shrink-0">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex gap-8">
              <div className="flex items-center gap-2">
                <i className="fas fa-cube text-cyan-400"></i>
                <span className="text-sm text-gray-400">Functions: <span className="text-white font-semibold">{funcCount}</span></span>
              </div>
              <div className="flex items-center gap-2">
                <i className="fas fa-times-circle text-red-400"></i>
                <span className="text-sm text-gray-400">Errors: <span className="text-white font-semibold">{errorCount}</span></span>
              </div>
              <div className="flex items-center gap-2">
                <i className="fas fa-lightbulb text-yellow-400"></i>
                <span className="text-sm text-gray-400">Improvements: <span className="text-white font-semibold">{improvementCount}</span></span>
              </div>
              <div className="flex items-center gap-2">
                <i className="fas fa-clock text-purple-400"></i>
                <span className="text-sm text-gray-400">Session: <span className="text-white font-semibold">{sessionTime}</span></span>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              Powered by <span className="text-blue-400 font-semibold">Gemini AI</span> • <span className="text-cyan-400 font-semibold">Neo4j</span> • <span className="text-purple-400 font-semibold">LangGraph</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
