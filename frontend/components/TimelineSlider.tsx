'use client';

import { useState } from 'react';
import { create } from 'zustand';

interface TimelineState {
  timestamp: number;
  setTimestamp: (ts: number) => void;
}

export const useTimelineStore = create<TimelineState>((set) => ({
  timestamp: 0,
  setTimestamp: (ts) => set({ timestamp: ts })
}));

export default function TimelineSlider() {
  const { timestamp, setTimestamp } = useTimelineStore();
  const [maxTime] = useState(100);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <h3 className="text-sm font-semibold mb-2">Time Travel Debugger</h3>
      <div className="flex items-center gap-4">
        <span className="text-xs text-gray-400">T={timestamp}</span>
        <input
          type="range"
          min="0"
          max={maxTime}
          value={timestamp}
          onChange={(e) => setTimestamp(Number(e.target.value))}
          className="flex-1"
        />
        <span className="text-xs text-gray-400">{maxTime}</span>
      </div>
    </div>
  );
}
