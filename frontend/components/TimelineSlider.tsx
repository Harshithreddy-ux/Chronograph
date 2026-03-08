'use client';

import { useState, useEffect } from 'react';

interface TimelineSliderProps {
  sessionId: string;
}

interface ExecutionEvent {
  timestamp: number;
  function: string;
  file: string;
  type: 'call' | 'return' | 'error';
  details?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function TimelineSlider({ sessionId }: TimelineSliderProps) {
  const [timestamp, setTimestamp] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [currentEvent, setCurrentEvent] = useState<ExecutionEvent | null>(null);
  const [maxTime, setMaxTime] = useState(100);

  useEffect(() => {
    if (!sessionId) return;

    // Fetch execution events from backend
    const fetchEvents = async () => {
      try {
        const response = await fetch(`${API_URL}/api/execution-timeline`);
        const data = await response.json();
        if (data.events && data.events.length > 0) {
          setEvents(data.events);
          setMaxTime(Math.max(...data.events.map((e: ExecutionEvent) => e.timestamp)));
        }
      } catch (error) {
        console.error('Failed to fetch timeline:', error);
      }
    };

    fetchEvents();
  }, [sessionId]);

  useEffect(() => {
    // Find current event based on timestamp
    const event = events.find(e => Math.abs(e.timestamp - timestamp) < 5);
    setCurrentEvent(event || null);
  }, [timestamp, events]);

  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setTimestamp(prev => {
        if (prev >= maxTime) {
          setIsPlaying(false);
          return maxTime;
        }
        return prev + 1;
      });
    }, 50);

    return () => clearInterval(interval);
  }, [isPlaying, maxTime]);

  const togglePlay = () => {
    if (timestamp >= maxTime) {
      setTimestamp(0);
    }
    setIsPlaying(!isPlaying);
  };

  const reset = () => {
    setTimestamp(0);
    setIsPlaying(false);
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'call': return '📞';
      case 'return': return '✅';
      case 'error': return '❌';
      default: return '⚡';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-gray-300">
          <i className="fas fa-history mr-2 text-purple-400"></i>
          Time-Travel Debugger
        </div>
        {events.length > 0 && (
          <div className="text-xs text-green-400 font-mono">
            {events.length} execution steps
          </div>
        )}
      </div>

      {events.length === 0 ? (
        <div className="text-xs text-gray-400 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-lg p-4">
          <div className="font-semibold text-purple-300 mb-2">
            🕐 What is Time-Travel Debugging?
          </div>
          <div className="space-y-2 text-xs leading-relaxed">
            <p>
              <span className="text-purple-400 font-semibold">Step through your code execution</span> like a movie! 
              See exactly which functions were called, in what order, and when errors occurred.
            </p>
            <p className="text-gray-500">
              Perfect for debugging race conditions, understanding async flows, and finding where things went wrong.
            </p>
            <p className="text-yellow-400 mt-3">
              📤 Upload code to see the execution timeline!
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-center gap-3">
            <button 
              onClick={togglePlay}
              className="w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 rounded-lg flex items-center justify-center transition shadow-lg hover:shadow-purple-500/50"
            >
              <i className={`fas fa-${isPlaying ? 'pause' : 'play'} text-white text-sm`}></i>
            </button>
            <button 
              onClick={reset}
              className="w-10 h-10 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center justify-center transition"
            >
              <i className="fas fa-redo text-white text-sm"></i>
            </button>
            <div className="flex-1 relative">
              <input 
                type="range" 
                min="0" 
                max={maxTime} 
                value={timestamp}
                onChange={(e) => setTimestamp(Number(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider-thumb"
                style={{
                  background: `linear-gradient(to right, #a855f7 0%, #a855f7 ${(timestamp/maxTime)*100}%, #374151 ${(timestamp/maxTime)*100}%, #374151 100%)`
                }}
              />
              <div className="flex justify-between mt-2 text-xs">
                <span className="text-gray-400">
                  T=<span className="text-purple-400 font-mono font-bold">{timestamp}</span>ms
                </span>
                <span className="text-gray-500">{maxTime}ms</span>
              </div>
            </div>
          </div>

          {currentEvent && (
            <div className="bg-gradient-to-br from-purple-900/50 to-indigo-900/40 border-2 border-purple-400/50 rounded-xl p-4 shadow-2xl">
              <div className="flex items-start gap-3">
                <div className="text-3xl animate-bounce">{getEventIcon(currentEvent.type)}</div>
                <div className="flex-1">
                  <div className="text-xs text-purple-300 font-semibold mb-1">
                    {currentEvent.type === 'call' ? '🎬 EXECUTING' : currentEvent.type === 'return' ? '✨ COMPLETED' : '💥 ERROR DETECTED'}
                  </div>
                  <div className="text-base font-bold text-white mb-1">
                    {currentEvent.function}()
                  </div>
                  <div className="text-xs text-gray-400 mb-2">
                    <i className="fas fa-file-code mr-1"></i>
                    {currentEvent.file}
                  </div>
                  {currentEvent.details && (
                    <div className="text-xs text-gray-200 mt-2 bg-black/40 rounded-lg px-3 py-2 font-mono border border-purple-500/30">
                      💡 {currentEvent.details}
                    </div>
                  )}
                  <div className="mt-3 text-xs text-purple-300 bg-purple-900/30 rounded px-2 py-1 inline-block">
                    ⏱️ T+{currentEvent.timestamp}ms
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-xs text-gray-400 mb-2 font-semibold">
              📜 Execution History
            </div>
            <div className="max-h-40 overflow-y-auto space-y-1 custom-scrollbar">
            >
              {events.map((event, idx) => (
                <div 
                  key={idx}
                  onClick={() => setTimestamp(event.timestamp)}
                  className={`text-xs p-2.5 rounded-lg cursor-pointer transition-all ${
                    Math.abs(event.timestamp - timestamp) < 5
                      ? 'bg-gradient-to-r from-purple-600/40 to-indigo-600/40 border-2 border-purple-400/60 scale-105 shadow-lg'
                      : 'bg-gray-700/40 hover:bg-gray-600/50 border border-gray-600/30'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-base">{getEventIcon(event.type)}</span>
                      <span className={`font-semibold ${
                        Math.abs(event.timestamp - timestamp) < 5 ? 'text-white' : 'text-gray-300'
                      }`}>
                        {event.function}()
                      </span>
                      {event.type === 'error' && (
                        <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full border border-red-500/30">
                          ERROR
                        </span>
                      )}
                    </div>
                    <span className="text-gray-400 font-mono text-xs">{event.timestamp}ms</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      <style jsx>{`
        .slider-thumb::-webkit-slider-thumb {
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
          cursor: pointer;
          box-shadow: 0 0 10px rgba(168, 85, 247, 0.8);
          transition: all 0.2s ease;
        }
        .slider-thumb::-webkit-slider-thumb:hover {
          transform: scale(1.2);
          box-shadow: 0 0 15px rgba(168, 85, 247, 1);
        }
        .slider-thumb::-moz-range-thumb {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
          cursor: pointer;
          border: none;
          box-shadow: 0 0 10px rgba(168, 85, 247, 0.8);
        }
        .animate-pulse-subtle {
          animation: pulse-subtle 2s ease-in-out infinite;
        }
        @keyframes pulse-subtle {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.95; }
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(31, 41, 55, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(168, 85, 247, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(168, 85, 247, 0.7);
        }
      `}</style>
    </div>
  );
}
