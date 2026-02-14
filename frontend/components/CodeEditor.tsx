'use client';

import Editor from '@monaco-editor/react';
import { useState } from 'react';

export default function CodeEditor() {
  const [code, setCode] = useState('# Select a function from the graph to view code');

  return (
    <div className="h-64 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <Editor
        height="100%"
        defaultLanguage="python"
        theme="vs-dark"
        value={code}
        onChange={(value) => setCode(value || '')}
        options={{
          minimap: { enabled: false },
          fontSize: 14
        }}
      />
    </div>
  );
}
