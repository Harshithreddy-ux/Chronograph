'use client';

import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  code: string;
  language?: string;
  selectedFunction?: string;
}

export default function CodeEditor({ code, language = 'python', selectedFunction }: CodeEditorProps) {
  return (
    <div className="h-full">
      <Editor
        height="100%"
        language={language}
        theme="vs-dark"
        value={code}
        options={{
          readOnly: true,
          minimap: { enabled: false },
          fontSize: 13,
          scrollBeyondLastLine: false,
          lineNumbers: 'on',
          renderLineHighlight: 'all',
          fontFamily: 'Consolas, Monaco, monospace',
          padding: { top: 16, bottom: 16 }
        }}
      />
    </div>
  );
}
