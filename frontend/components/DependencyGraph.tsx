'use client';

import { useEffect, useState } from 'react';
import { ReactFlow, Node, Edge, Background, Controls, BackgroundVariant } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface DependencyGraphProps {
  sessionId: string;
  onNodeClick: (nodeData: any) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `http://${window.location.hostname}:8000` : 'http://localhost:8000');

export default function DependencyGraph({ sessionId, onNodeClick }: DependencyGraphProps) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (!sessionId) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const fetchGraph = async () => {
      try {
        const response = await fetch(`${API_URL}/api/graph`);
        const data = await response.json();
        
        console.log('Graph data:', data);
        
        // Separate files and functions
        const fileNodes = data.nodes.filter((node: any) => node.type === 'File');
        const functionNodes = data.nodes.filter((node: any) => node.type === 'Function');
        
        console.log('Files:', fileNodes.length, 'Functions:', functionNodes.length);
        
        // Group functions by file
        const functionsByFile = new Map();
        data.edges
          .filter((edge: any) => edge.type === 'CONTAINS')
          .forEach((edge: any) => {
            const fileNode = fileNodes.find((n: any) => String(n.id) === String(edge.source));
            const funcNode = functionNodes.find((n: any) => String(n.id) === String(edge.target));
            if (fileNode && funcNode) {
              const filePath = fileNode.path || fileNode.name;
              if (!functionsByFile.has(filePath)) {
                functionsByFile.set(filePath, []);
              }
              functionsByFile.get(filePath).push(funcNode);
            }
          });
        
        console.log('Functions by file:', Array.from(functionsByFile.entries()).map(([k, v]) => `${k}: ${v.length} functions`));
        
        // SIMPLE LAYOUT: Each file gets a column, functions stack vertically below
        const COLUMN_WIDTH = 450;  // Increased from 350
        const FILE_Y = 50;
        const FUNCTION_START_Y = 200;  // Increased from 180
        const FUNCTION_SPACING = 140;  // Increased from 100
        
        // Create file nodes at the top (one per column)
        const flowFileNodes = fileNodes.map((node: any, idx: number) => ({
          id: `file-${node.path}`,
          data: { 
            label: node.path || node.name,
            fullData: node
          },
          position: { 
            x: 50 + idx * COLUMN_WIDTH,
            y: FILE_Y
          },
          style: {
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            border: '3px solid #34d399',
            borderRadius: '12px',
            padding: '16px 24px',
            fontSize: '15px',
            fontWeight: '700',
            boxShadow: '0 6px 16px rgba(16, 185, 129, 0.5)',
            minWidth: '220px',
            textAlign: 'center'
          }
        }));
        
        // Create function nodes in columns below their files
        const flowFunctionNodes: any[] = [];
        const functionNodeMap = new Map(); // Track function nodes for call edges
        
        Array.from(functionsByFile.entries()).forEach(([filePath, functions], fileIdx) => {
          functions.forEach((node: any, funcIdx: number) => {
            const hasError = node.has_error === true;
            const hasImprovement = node.has_improvement === true;
            
            const nodeId = `func-${node.name}-${node.file_path}`;
            
            flowFunctionNodes.push({
              id: nodeId,
              data: { 
                label: node.name,
                fullData: node
              },
              position: { 
                x: 50 + fileIdx * COLUMN_WIDTH,
                y: FUNCTION_START_Y + funcIdx * FUNCTION_SPACING
              },
              style: {
                background: hasError
                  ? 'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)'
                  : hasImprovement
                    ? 'linear-gradient(135deg, #78350f 0%, #92400e 100%)'
                    : 'linear-gradient(135deg, #1f2937 0%, #374151 100%)',
                color: 'white',
                border: hasError 
                  ? '3px solid #ef4444' 
                  : hasImprovement 
                    ? '3px solid #fbbf24'
                    : '2px solid #6b7280',
                borderRadius: '12px',
                padding: '14px 22px',
                fontSize: '14px',
                fontWeight: '600',
                boxShadow: hasError
                  ? '0 0 30px rgba(239, 68, 68, 0.7), 0 8px 16px rgba(0, 0, 0, 0.4)'
                  : hasImprovement
                    ? '0 0 30px rgba(251, 191, 36, 0.7), 0 8px 16px rgba(0, 0, 0, 0.4)'
                    : '0 6px 12px rgba(0, 0, 0, 0.4)',
                minWidth: '200px',
                textAlign: 'center',
                transition: 'all 0.3s ease'
              }
            });
            
            // Store for call edge lookup
            functionNodeMap.set(node.id, { nodeId, name: node.name, filePath: node.file_path });
          });
        });
        
        // Combine all nodes
        const allNodes = [...flowFileNodes, ...flowFunctionNodes];
        
        // EDGE 1: File -> Functions (GREEN, smooth bezier curves)
        const fileToFuncEdges: any[] = [];
        
        Array.from(functionsByFile.entries()).forEach(([filePath, functions]) => {
          functions.forEach((node: any) => {
            fileToFuncEdges.push({
              id: `contains-${filePath}-${node.name}`,
              source: `file-${filePath}`,
              target: `func-${node.name}-${node.file_path}`,
              type: 'default', // Smooth bezier curve
              animated: false,
              style: { 
                stroke: '#34d399',
                strokeWidth: 2.5,
                strokeDasharray: '5,5'
              },
              markerEnd: {
                type: 'arrowclosed',
                color: '#34d399',
                width: 20,
                height: 20
              }
            });
          });
        });
        
        // EDGE 2: Function -> Function calls (PURPLE, beautiful smooth curves)
        const callEdges = data.edges
          .filter((edge: any) => edge.type === 'CALLS')
          .map((edge: any) => {
            const sourceInfo = functionNodeMap.get(edge.source);
            const targetInfo = functionNodeMap.get(edge.target);
            
            if (!sourceInfo || !targetInfo) {
              console.log('Missing function for call edge:', edge);
              return null;
            }
            
            console.log(`Call edge: ${sourceInfo.name} -> ${targetInfo.name}`);
            
            return {
              id: `call-${sourceInfo.name}-${targetInfo.name}-${Date.now()}`,
              source: sourceInfo.nodeId,
              target: targetInfo.nodeId,
              type: 'default', // Smooth bezier curve
              animated: true,
              style: { 
                stroke: '#a855f7',
                strokeWidth: 3
              },
              markerEnd: {
                type: 'arrowclosed',
                color: '#a855f7',
                width: 25,
                height: 25
              },
              label: '⚡ calls',
              labelStyle: { 
                fill: '#e9d5ff', 
                fontWeight: 700, 
                fontSize: 12,
                textShadow: '0 0 10px rgba(168, 85, 247, 0.8)'
              },
              labelBgStyle: { 
                fill: '#581c87', 
                fillOpacity: 0.95,
                rx: 8,
                ry: 8
              },
              labelBgPadding: [8, 12] as [number, number]
            };
          })
          .filter(Boolean);
        
        console.log('Call edges:', callEdges.length);
        
        const allEdges = [...fileToFuncEdges, ...callEdges];
        
        setNodes(allNodes);
        setEdges(allEdges);
      } catch (error) {
        console.error('Graph fetch error:', error);
      }
    };

    fetchGraph();
  }, [sessionId]);

  const handleNodeClick = (_event: any, node: Node) => {
    onNodeClick(node.data.fullData);
  };

  return (
    <div className="h-full w-full bg-gray-900/50 rounded-lg overflow-hidden">
      <style jsx global>{`
        /* ReactFlow Controls Styling */
        .react-flow__controls {
          background: rgba(31, 41, 55, 0.9) !important;
          border: 1px solid rgba(75, 85, 99, 0.5) !important;
          border-radius: 8px !important;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        }
        .react-flow__controls button {
          background: rgba(55, 65, 81, 0.8) !important;
          border-bottom: 1px solid rgba(75, 85, 99, 0.3) !important;
          color: #9ca3af !important;
          width: 28px !important;
          height: 28px !important;
        }
        .react-flow__controls button:hover {
          background: rgba(75, 85, 99, 0.9) !important;
          color: #fff !important;
        }
        .react-flow__controls button svg {
          max-width: 14px !important;
          max-height: 14px !important;
        }
        
        /* Attribution */
        .react-flow__attribution {
          background: rgba(31, 41, 55, 0.8) !important;
          color: #6b7280 !important;
          font-size: 10px !important;
          padding: 2px 6px !important;
          border-radius: 4px !important;
        }
        
        /* Custom scrollbar */
        .react-flow__pane::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .react-flow__pane::-webkit-scrollbar-track {
          background: rgba(31, 41, 55, 0.5);
          border-radius: 4px;
        }
        .react-flow__pane::-webkit-scrollbar-thumb {
          background: rgba(107, 114, 128, 0.5);
          border-radius: 4px;
        }
        .react-flow__pane::-webkit-scrollbar-thumb:hover {
          background: rgba(156, 163, 175, 0.7);
        }
      `}</style>
      {nodes.length === 0 && !sessionId ? (
        <div className="h-full flex items-center justify-center text-gray-400">
          <div className="text-center">
            <i className="fas fa-upload text-4xl mb-3 opacity-50"></i>
            <p className="text-sm">Upload code to see dependency graph</p>
          </div>
        </div>
      ) : (
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={handleNodeClick}
          fitView
          className="rounded-lg"
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#374151" />
          <Controls />
        </ReactFlow>
      )}
    </div>
  );
}
