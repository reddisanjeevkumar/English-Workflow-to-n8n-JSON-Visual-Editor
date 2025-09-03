import React, { useState } from 'react';
import axios from 'axios';
import ReactFlow, { MiniMap, Controls, Background, applyNodeChanges, applyEdgeChanges } from 'react-flow-renderer';

// Defensive converter from n8n workflow JSON to React Flow format
function n8nToReactFlow(workflowJson) {
  if (!workflowJson?.nodes) return { nodes: [], edges: [] };

  // Defensive node mapping
  const nodes = workflowJson.nodes.map((node, i) => {
    let position = node.position;
    if (
      !position ||
      typeof position !== "object" ||
      typeof position.x !== "number" ||
      typeof position.y !== "number"
    ) {
      position = { x: 80 + i * 180, y: 120 };
    }
    return {
      id: node.id || node.name || `node-${i}`,
      data: { label: node.id || node.name || `Node ${i + 1}` },
      position,
      type: node.type || 'default',
    };
  });

  // Defensive edge mapping
  const validNodeIds = new Set(nodes.map(n => n.id));
  const edges = [];
  if (workflowJson.connections) {
    Object.entries(workflowJson.connections).forEach(([fromId, conns]) => {
      let mainConns = conns.main;
      if (Array.isArray(mainConns) && mainConns.length && !Array.isArray(mainConns[0])) {
        mainConns = [mainConns];
      }
      if (Array.isArray(mainConns)) {
        mainConns.forEach(connArr => {
          connArr.forEach(conn => {
            const sourceId = fromId;
            const targetId = conn.node;
            if (validNodeIds.has(sourceId) && validNodeIds.has(targetId)) {
              edges.push({
                id: `${sourceId}-${targetId}`,
                source: sourceId,
                target: targetId,
                animated: true,
              });
            }
          });
        });
      }
    });
  }
  return { nodes, edges };
}

export default function App() {
  const [description, setDescription] = useState('');
  const [workflowJson, setWorkflowJson] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);

  // Generate workflow and update nodes/edges state
  const generateWorkflow = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:5000/api/generate-workflow', { description });
      setWorkflowJson(res.data);
      const { nodes, edges } = n8nToReactFlow(res.data);
      setNodes(nodes);
      setEdges(edges);
    } catch (e) {
      alert('Error: ' + (e.response?.data?.error || e.message));
    }
    setLoading(false);
  };

  // Correct change handlers as per React Flow docs
  const onNodesChange = changes => setNodes(nds => applyNodeChanges(changes, nds));
  const onEdgesChange = changes => setEdges(eds => applyEdgeChanges(changes, eds));

  // Handle JSON edit and update nodes/edges
  const handleJsonEdit = e => {
    try {
      const json = JSON.parse(e.target.value);
      setWorkflowJson(json);
      const { nodes, edges } = n8nToReactFlow(json);
      setNodes(nodes);
      setEdges(edges);
    } catch {}
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(workflowJson, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'workflow.json';
    a.click();
  };

  return (
    <div style={{ display: 'flex', gap: 40, padding: 30 }}>
      <div style={{ width: 400 }}>
        <h2>English Workflow Description</h2>
        <textarea
          rows={7}
          style={{ width: '100%' }}
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="Start, fetch user data, send email, etc."
        />
        <br />
        <button onClick={generateWorkflow} disabled={loading}>
          {loading ? 'Loading...' : 'Generate Workflow'}
        </button>
        <br />
        <h3>Edit Workflow JSON</h3>
        <textarea
          rows={14}
          style={{ width: '100%', fontFamily: 'monospace', fontSize: 15 }}
          value={workflowJson ? JSON.stringify(workflowJson, null, 2) : ''}
          onChange={handleJsonEdit}
        />
        <br />
        <button onClick={downloadJSON} disabled={!workflowJson}>Download JSON</button>
      </div>
      <div style={{ flex: 1, height: 600 }}>
        <h2>Visual Workflow Editor</h2>
        <div style={{ height: 550, border: '1px solid #ccc', borderRadius: 8 }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}