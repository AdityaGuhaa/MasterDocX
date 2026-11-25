// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { FaSearch, FaBrain, FaProjectDiagram, FaVolumeUp } from 'react-icons/fa';
import { Network } from 'vis-network/standalone';
import './DocumentViewer.css';

// Helper: convert hierarchical mindmap JSON into vis-network nodes/edges
const mindmapToGraph = (data) => {
  const nodes = [];
  const edges = [];
  let idCounter = 1;

  const traverse = (node, parentId) => {
    const currentId = idCounter++;
    nodes.push({
      id: currentId,
      label: node.title || node.label || 'Untitled',
      level: parentId === null ? 0 : undefined,
      font: parentId === null ? { size: 18, bold: true } : { size: 14 },
    });
    if (parentId !== null) {
      edges.push({ from: parentId, to: currentId });
    }
    if (node.children && Array.isArray(node.children)) {
      node.children.forEach((child) => traverse(child, currentId));
    }
  };

  traverse(data, null);
  return { nodes, edges };
};

const DocumentViewer = () => {
  const { docId } = useParams();
  const [documentInfo, setDocumentInfo] = useState(null);
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [summary, setSummary] = useState('');
  const [explanationText, setExplanationText] = useState('');
  const [explanationResult, setExplanationResult] = useState('');
  const [mindmap, setMindmap] = useState(null);
  const [knowledgeGraph, setKnowledgeGraph] = useState(null);
  const [activeTab, setActiveTab] = useState('info');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const mindmapContainerRef = useRef(null);
  const graphContainerRef = useRef(null);
  const mindmapNetworkRef = useRef(null);
  const graphNetworkRef = useRef(null);

  useEffect(() => {
    fetchDocumentInfo();
  }, [docId]);

  // Render mindmap when data arrives
  useEffect(() => {
    if (mindmap && mindmapContainerRef.current && activeTab === 'mindmap') {
      const { nodes, edges } = mindmapToGraph(mindmap);
      const options = {
        layout: { hierarchical: { direction: 'UD', sortMethod: 'directed', levelSeparation: 120, nodeSpacing: 160 } },
        nodes: { shape: 'box', margin: 10, borderWidth: 2, color: { background: '#e3f2fd', border: '#2196f3', highlight: { background: '#bbdefb', border: '#1976d2' } }, font: { face: 'Segoe UI, sans-serif' } },
        edges: { color: { color: '#90caf9' }, arrows: { to: { enabled: true, scaleFactor: 0.5 } }, smooth: { type: 'cubicBezier' } },
        physics: false,
        interaction: { dragNodes: true, zoomView: true, dragView: true },
      };
      if (mindmapNetworkRef.current) mindmapNetworkRef.current.destroy();
      mindmapNetworkRef.current = new Network(mindmapContainerRef.current, { nodes, edges }, options);
    }
  }, [mindmap, activeTab]);

  // Render knowledge graph when data arrives
  useEffect(() => {
    if (knowledgeGraph && graphContainerRef.current && activeTab === 'graph') {
      const nodes = (knowledgeGraph.nodes || []).map((n) => ({
        id: n.id,
        label: n.label,
        shape: 'dot',
        size: 20,
        color: { background: '#c8e6c9', border: '#43a047', highlight: { background: '#a5d6a7', border: '#2e7d32' } },
        font: { size: 14, face: 'Segoe UI, sans-serif' },
      }));
      const edges = (knowledgeGraph.edges || []).map((e) => ({
        from: e.source,
        to: e.target,
        label: e.label || '',
        color: { color: '#81c784' },
        arrows: { to: { enabled: true, scaleFactor: 0.5 } },
        font: { size: 11, align: 'middle', color: '#555' },
        smooth: { type: 'curvedCW', roundness: 0.2 },
      }));
      const options = {
        physics: { solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: -50, springLength: 150 } },
        interaction: { hover: true, tooltipDelay: 200 },
      };
      if (graphNetworkRef.current) graphNetworkRef.current.destroy();
      graphNetworkRef.current = new Network(graphContainerRef.current, { nodes, edges }, options);
    }
  }, [knowledgeGraph, activeTab]);

  // Cleanup networks on unmount
  useEffect(() => {
    return () => {
      if (mindmapNetworkRef.current) mindmapNetworkRef.current.destroy();
      if (graphNetworkRef.current) graphNetworkRef.current.destroy();
    };
  }, []);

  const fetchDocumentInfo = async () => {
    try {
      const response = await axios.get(`/api/v1/document/${docId}`);
      setDocumentInfo(response.data);
    } catch (err) {
      setError('Failed to fetch document info: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsLoading(true);
    setError('');
    setAnswer('');
    try {
      const response = await axios.post('/api/v1/query', { doc_id: docId, query });
      setAnswer(response.data.response);
    } catch (err) {
      setError('Failed to query document: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSummarize = async () => {
    setIsLoading(true);
    setError('');
    setSummary('');
    try {
      const response = await axios.post('/api/v1/summarize', { doc_id: docId });
      setSummary(response.data.summary);
    } catch (err) {
      setError('Failed to generate summary: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleExplain = async (e) => {
    e.preventDefault();
    if (!explanationText.trim()) return;
    setIsLoading(true);
    setError('');
    setExplanationResult('');
    try {
      const response = await axios.post('/api/v1/explain', { doc_id: docId, text: explanationText });
      setExplanationResult(response.data.explanation);
    } catch (err) {
      setError('Failed to explain text: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleMindmap = async () => {
    setIsLoading(true);
    setError('');
    setMindmap(null);
    try {
      const response = await axios.get(`/api/v1/mindmap/${docId}`);
      setMindmap(response.data.mindmap);
    } catch (err) {
      setError('Failed to generate mindmap: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKnowledgeGraph = async () => {
    setIsLoading(true);
    setError('');
    setKnowledgeGraph(null);
    try {
      const response = await axios.get(`/api/v1/knowledge-graph/${docId}`);
      setKnowledgeGraph(response.data.knowledge_graph);
    } catch (err) {
      setError('Failed to generate knowledge graph: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextToSpeech = async (text) => {
    try {
      const response = await axios.post('/api/v1/tts', { doc_id: docId, text }, { responseType: 'blob' });
      const audioUrl = URL.createObjectURL(new Blob([response.data], { type: 'audio/wav' }));
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (err) {
      setError('Failed to generate speech: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (!documentInfo) {
    return (
      <div className="document-viewer">
        <h2>Loading Document...</h2>
        {error && <div className="error">{error}</div>}
      </div>
    );
  }

  return (
    <div className="document-viewer">
      <h2>Document: {documentInfo.file_name || docId}</h2>
      {error && <div className="error">{error}</div>}

      <div className="document-tabs">
        <button className={activeTab === 'info' ? 'active' : ''} onClick={() => setActiveTab('info')}>Info</button>
        <button className={activeTab === 'query' ? 'active' : ''} onClick={() => setActiveTab('query')}><FaSearch /> Query</button>
        <button className={activeTab === 'summary' ? 'active' : ''} onClick={() => { setActiveTab('summary'); if (!summary) handleSummarize(); }}><FaBrain /> Summary</button>
        <button className={activeTab === 'explain' ? 'active' : ''} onClick={() => setActiveTab('explain')}>Explain</button>
        <button className={activeTab === 'mindmap' ? 'active' : ''} onClick={() => { setActiveTab('mindmap'); if (!mindmap) handleMindmap(); }}><FaProjectDiagram /> Mindmap</button>
        <button className={activeTab === 'graph' ? 'active' : ''} onClick={() => { setActiveTab('graph'); if (!knowledgeGraph) handleKnowledgeGraph(); }}>Knowledge Graph</button>
      </div>

      <div className="tab-content">
        {activeTab === 'info' && (
          <div className="info-tab">
            <h3>Document Information</h3>
            <div className="info-grid">
              <div><strong>ID:</strong> {documentInfo.doc_id}</div>
              <div><strong>File Name:</strong> {documentInfo.file_name}</div>
              <div><strong>Processed At:</strong> {documentInfo.processed_at}</div>
              <div><strong>Chunk Count:</strong> {documentInfo.chunk_count}</div>
              <div><strong>Character Count:</strong> {documentInfo.character_count}</div>
              <div><strong>Hash:</strong> {documentInfo.hash}</div>
            </div>
            {documentInfo.summary && (
              <div className="summary-preview">
                <h4>Summary Preview:</h4>
                <p>{documentInfo.summary.substring(0, 200)}...</p>
                <button onClick={() => { setActiveTab('summary'); if (!summary) handleSummarize(); }}>View Full Summary</button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'query' && (
          <div className="query-tab">
            <h3>Ask Questions About This Document</h3>
            <form onSubmit={handleQuery}>
              <div className="input-group">
                <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Enter your question about the document..." disabled={isLoading} />
                <button type="submit" disabled={isLoading || !query.trim()}>{isLoading ? 'Searching...' : 'Ask'}</button>
              </div>
            </form>
            {answer && (
              <div className="answer-result">
                <h4>Answer:</h4>
                <div className="answer-content">
                  {answer}
                  <button className="tts-button" onClick={() => handleTextToSpeech(answer)} title="Listen to answer"><FaVolumeUp /></button>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="summary-tab">
            <h3>Document Summary</h3>
            {isLoading ? (
              <div className="loading-indicator">Generating summary...</div>
            ) : summary ? (
              <div className="summary-content">
                <p>{summary}</p>
                <button className="tts-button" onClick={() => handleTextToSpeech(summary)} title="Listen to summary"><FaVolumeUp /> Listen</button>
              </div>
            ) : (
              <button onClick={handleSummarize}>Generate Summary</button>
            )}
          </div>
        )}

        {activeTab === 'explain' && (
          <div className="explain-tab">
            <h3>Explain Text</h3>
            <form onSubmit={handleExplain}>
              <textarea value={explanationText} onChange={(e) => setExplanationText(e.target.value)} placeholder="Enter text you want explained..." rows="4" disabled={isLoading} />
              <button type="submit" disabled={isLoading || !explanationText.trim()}>{isLoading ? 'Explaining...' : 'Explain'}</button>
            </form>
            {explanationResult && (
              <div className="explanation-result">
                <h4>Explanation:</h4>
                <div className="explanation-content">
                  {explanationResult}
                  <button className="tts-button" onClick={() => handleTextToSpeech(explanationResult)} title="Listen to explanation"><FaVolumeUp /></button>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'mindmap' && (
          <div className="mindmap-tab">
            <h3>Document Mindmap</h3>
            {isLoading ? (
              <div className="loading-indicator">Generating mindmap...</div>
            ) : mindmap ? (
              <div className="mindmap-content">
                <div ref={mindmapContainerRef} className="vis-container" />
              </div>
            ) : (
              <button onClick={handleMindmap}>Generate Mindmap</button>
            )}
          </div>
        )}

        {activeTab === 'graph' && (
          <div className="graph-tab">
            <h3>Knowledge Graph</h3>
            {isLoading ? (
              <div className="loading-indicator">Generating knowledge graph...</div>
            ) : knowledgeGraph ? (
              <div className="graph-content">
                <div ref={graphContainerRef} className="vis-container" />
              </div>
            ) : (
              <button onClick={handleKnowledgeGraph}>Generate Knowledge Graph</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;