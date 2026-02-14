'use client';

import { useEffect, useState } from 'react';
import { ReactFlow, Node, Edge, Background, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface DependencyGraphProps {
  sessionId: string;
}

export default function DependencyGraph({ sessionId }: DependencyGraphProps) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (!sessionId) return;

    // Mock data for demo
    const mockNodes = [
      { id: '1', data: { label: 'main.py' }, position: { x: 100, y: 50 } },
      { id: '2', data: { label: 'handle_request()' }, position: { x: 100, y: 150 } },
      { id: '3', data: { label: 'db_save()' }, position: { x: 300, y: 150 } },
      { id: '4', data: { label: 'process_data()' }, position: { x: 100, y: 250 } },
      { id: '5', data: { label: 'validate()' }, position: { x: 300, y: 250 } },
    ];

    const mockEdges = [
      { id: 'e1-2', source: '1', target: '2', label: 'CONTAINS' },
      { id: 'e2-3', source: '2', target: '3', label: 'CALLS' },
      { id: 'e2-4', source: '2', target: '4', label: 'CALLS' },
      { id: 'e4-5', source: '4', target: '5', label: 'CALLS' },
    ];

    setNodes(mockNodes);
    setEdges(mockEdges);
  }, [sessionId]);

  return (
    <div className="h-96 bg-gray-800 rounded-lg border border-gray-700">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
