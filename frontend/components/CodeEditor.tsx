'use client';

import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  code: string;
  language?: string;
  selectedFunction?: string;
}

export default function CodeEditor({ code, language = 'python', selectedFunction }: CodeEditorProps) {
  return (
    <div className="h-64 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="bg-gray-900 px-4 py-2 border-b border-gray-700">
        <span className="text-sm text-gray-400">
          {selectedFunction ? `Function: ${selectedFunction}` : 'Select a function from the graph'}
        </span>
      </div>
      <Editor
        height="calc(100% - 40px)"
        language={language}
        theme="vs-dark"
        value={code}
        options={{
          readOnly: true,
          minimap: { enabled: false },
          fontSize: 14,
          scrollBeyondLastLine: false
        }}
      />
    </div>
  );
}
