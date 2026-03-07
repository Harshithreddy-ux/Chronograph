'use client';

import { useEffect, useState } from 'react';
import { ReactFlow, Node, Edge, Background, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface DependencyGraphProps {
  sessionId: string;
  onNodeClick: (nodeData: any) => void;
}

export default function DependencyGraph({ sessionId, onNodeClick }: DependencyGraphProps) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (!sessionId) return;

    // Fetch real graph data from backend
    const fetchGraph = async () => {
      try {
        const response = await fetch('http://35.172.115.54:8000/api/graph');
        const data = await response.json();
        
        // Convert Neo4j data to React Flow format
        const flowNodes = data.nodes.map((node: any, idx: number) => ({
          id: String(node.id),
          data: { 
            label: node.name || node.path,
            fullData: node // Store full node data
          },
          position: { x: 100 + (idx % 3) * 200, y: 50 + Math.floor(idx / 3) * 100 },
          style: {
            background: node.type === 'Function' ? '#3b82f6' : '#10b981',
            color: 'white',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            padding: '10px'
          }
        }));
        
        const flowEdges = data.edges.map((edge: any) => ({
          id: `e${edge.source}-${edge.target}`,
          source: String(edge.source),
          target: String(edge.target),
          label: edge.type,
          animated: true
        }));
        
        setNodes(flowNodes);
        setEdges(flowEdges);
      } catch (error) {
        console.error('Graph fetch error:', error);
      }
    };

    fetchGraph();
  }, [sessionId]);

  const handleNodeClick = (_event: any, node: Node) => {
    // Fetch full function details when clicked
    onNodeClick(node.data.fullData);
  };

  return (
    <div className="h-96 bg-gray-800 rounded-lg border border-gray-700">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={handleNodeClick}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
