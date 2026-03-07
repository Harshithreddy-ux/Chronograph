'use client';

import { useState } from 'react';

export default function TimelineSlider() {
  const [timestamp, setTimestamp] = useState(0);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 h-32">
      <div className="mb-2">
        <span className="text-sm font-semibold text-gray-300">
          Execution Timeline
        </span>
        <span className="text-xs text-gray-500 ml-2">(Coming Soon)</span>
      </div>
      <div className="text-xs text-gray-500 mb-3">
        Will show code execution flow over time for debugging race conditions
      </div>
      <div className="flex items-center gap-4">
        <button className="text-xs bg-gray-700 px-3 py-1 rounded opacity-50 cursor-not-allowed">
          ▶ Play
        </button>
        <input
          type="range"
          min="0"
          max="100"
          value={timestamp}
          onChange={(e) => setTimestamp(Number(e.target.value))}
          className="flex-1 opacity-50"
          disabled
        />
        <span className="text-sm text-gray-400">{timestamp}ms</span>
      </div>
    </div>
  );
}
