// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import {
  FiInfo,
  FiMessageCircle,
  FiAlignLeft,
  FiZap,
  FiGitBranch,
  FiShare2,
  FiVolume2,
  FiSquare,
  FiArrowUp,
  FiAlertCircle,
  FiMaximize2,
  FiRotateCcw,
} from 'react-icons/fi';
import { Network } from 'vis-network/standalone';
import { useTheme } from '../theme';
import './DocumentViewer.css';

const TABS = [
  { id: 'info', label: 'Overview', icon: FiInfo },
  { id: 'query', label: 'Ask', icon: FiMessageCircle },
  { id: 'summary', label: 'Summary', icon: FiAlignLeft },
  { id: 'explain', label: 'Explain', icon: FiZap },
  { id: 'mindmap', label: 'Mindmap', icon: FiGitBranch },
  { id: 'graph', label: 'Graph', icon: FiShare2 },
];

const SUGGESTIONS = ['What is this document about?', 'What are the key points?', 'What conclusions does it reach?'];

// Read a design token so the graphs match light and dark mode
const token = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const FONT_FACE = '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif';
const MIN_READABLE_SCALE = 0.75;

// Models don't always follow the {title, children} format: branches can be plain strings,
// use other keys (name, text, topic...), or be {"Topic": [...]} objects. Normalise them.
const LABEL_KEYS = ['title', 'label', 'name', 'text', 'topic', 'node'];
const CHILD_KEYS = ['children', 'subtopics', 'items', 'nodes', 'branches'];

const normalizeNode = (node) => {
  if (node === null || node === undefined) return { title: 'Untitled', children: [] };
  if (typeof node !== 'object') return { title: String(node), children: [] };
  if (Array.isArray(node)) return { title: 'Untitled', children: node };

  const labelKey = LABEL_KEYS.find((k) => typeof node[k] === 'string' && node[k].trim());
  const childKey = CHILD_KEYS.find((k) => Array.isArray(node[k]));
  if (labelKey || childKey) {
    return { title: labelKey ? node[labelKey] : 'Untitled', children: childKey ? node[childKey] : [] };
  }

  // {"Topic": [...]} or {"Topic": "detail"}
  const entries = Object.entries(node);
  if (entries.length === 1) {
    const [key, value] = entries[0];
    if (Array.isArray(value)) return { title: key, children: value };
    if (typeof value === 'string') return { title: `${key}: ${value}`, children: [] };
    return { title: key, children: [value] };
  }
  return { title: 'Untitled', children: entries.map(([key, value]) => ({ [key]: value })) };
};

// Helper: convert hierarchical mindmap JSON into vis-network nodes/edges
const mindmapToGraph = (data) => {
  const nodes = [];
  const edges = [];
  let idCounter = 1;

  const traverse = (rawNode, parentId, depth) => {
    const node = normalizeNode(rawNode);
    const currentId = idCounter++;
    const isRoot = parentId === null;
    nodes.push({
      id: currentId,
      label: node.title,
      level: depth,
      color: isRoot
        ? { background: token('--accent'), border: token('--accent'), highlight: { background: token('--accent'), border: token('--accent') } }
        : { background: token('--surface'), border: token('--hairline'), highlight: { background: token('--surface'), border: token('--accent') } },
      font: isRoot
        ? { size: 17, color: '#ffffff', face: FONT_FACE, bold: { color: '#ffffff' } }
        : { size: 14, color: token('--text'), face: FONT_FACE },
    });
    if (!isRoot) {
      edges.push({ from: parentId, to: currentId });
    }
    if (node.children && Array.isArray(node.children)) {
      node.children.forEach((child) => traverse(child, currentId, depth + 1));
    }
  };

  traverse(data, null, 0);
  return { nodes, edges };
};

// Render the model's light markdown (**bold**, bullet lists, headings) as real formatting
const renderInline = (text) =>
  text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.length > 4 && part.startsWith('**') && part.endsWith('**') ? <strong key={i}>{part.slice(2, -2)}</strong> : part
  );

const RichText = ({ text }) => {
  const blocks = [];
  let list = null;
  text.split('\n').forEach((raw) => {
    const line = raw.trim();
    const bullet = line.match(/^(?:[-*•]|\d+[.)])\s+(.*)$/);
    if (bullet) {
      if (!list) {
        list = { type: /^\d/.test(line) ? 'ol' : 'ul', items: [] };
        blocks.push(list);
      }
      const indent = raw.length - raw.trimStart().length;
      list.items.push({ text: bullet[1], nested: indent >= 2 });
      return;
    }
    list = null;
    if (!line) return;
    const heading = line.match(/^#{1,6}\s+(.*)$/);
    blocks.push(heading ? { type: 'h', text: heading[1] } : { type: 'p', text: line });
  });

  return (
    <div className="rich-text">
      {blocks.map((block, i) => {
        if (block.type === 'p') return <p key={i}>{renderInline(block.text)}</p>;
        if (block.type === 'h') return <h4 key={i}>{renderInline(block.text)}</h4>;
        const List = block.type;
        return (
          <List key={i}>
            {block.items.map((item, j) => (
              <li key={j} className={item.nested ? 'nested' : undefined}>
                {renderInline(item.text)}
              </li>
            ))}
          </List>
        );
      })}
    </div>
  );
};

const Thinking = ({ label, hint }) => (
  <div className="thinking fade">
    <div className="thinking-label">
      <span className="spinner" /> {label}
    </div>
    {hint && <p className="thinking-hint">{hint}</p>}
    <div className="skeleton" style={{ width: '92%' }} />
    <div className="skeleton" style={{ width: '80%' }} />
    <div className="skeleton" style={{ width: '64%' }} />
  </div>
);

const formatDate = (iso) => {
  if (!iso) return '—';
  const date = new Date(iso);
  return Number.isNaN(date.getTime())
    ? iso
    : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
};

const DocumentViewer = () => {
  const { docId } = useParams();
  const [documentInfo, setDocumentInfo] = useState(null);
  const [query, setQuery] = useState('');
  const [thread, setThread] = useState([]); // [{ question, answer }]; answer is null while waiting
  const [summary, setSummary] = useState('');
  const [explanationText, setExplanationText] = useState('');
  const [explanationResult, setExplanationResult] = useState('');
  const [mindmap, setMindmap] = useState(null);
  const [knowledgeGraph, setKnowledgeGraph] = useState(null);
  const [activeTab, setActiveTab] = useState('info');
  const [busy, setBusy] = useState({});
  const [speaking, setSpeaking] = useState(null);
  const [error, setError] = useState('');
  const [theme] = useTheme(); // graphs are redrawn in the new colours when the theme changes

  const mindmapContainerRef = useRef(null);
  const graphContainerRef = useRef(null);
  const mindmapNetworkRef = useRef(null);
  const graphNetworkRef = useRef(null);
  const audioRef = useRef(null);
  const askInputRef = useRef(null);
  const threadEndRef = useRef(null);

  const setTaskBusy = (task, value) => setBusy((current) => ({ ...current, [task]: value }));

  useEffect(() => {
    setThread([]);
    fetchDocumentInfo();
  }, [docId]);

  // Keep the newest question and answer in view, and the cursor ready for a follow-up
  useEffect(() => {
    if (activeTab !== 'query' || thread.length === 0) return;
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    if (!busy.query) askInputRef.current?.focus({ preventScroll: true });
  }, [thread, busy.query, activeTab]);

  // Render mindmap when data arrives
  useEffect(() => {
    if (mindmap && mindmapContainerRef.current && activeTab === 'mindmap') {
      const { nodes, edges } = mindmapToGraph(mindmap);
      const options = {
        layout: {
          hierarchical: { direction: 'LR', sortMethod: 'directed', levelSeparation: 250, nodeSpacing: 56, treeSpacing: 80 },
        },
        nodes: {
          shape: 'box',
          margin: { top: 10, right: 14, bottom: 10, left: 14 },
          borderWidth: 1,
          shapeProperties: { borderRadius: 10 },
          widthConstraint: { maximum: 220 },
          shadow: { enabled: true, color: 'rgba(0,0,0,0.06)', size: 12, x: 0, y: 3 },
        },
        edges: {
          color: { color: token('--text-3'), opacity: 0.45 },
          width: 1.2,
          smooth: { type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.5 },
          arrows: { to: { enabled: false } },
        },
        physics: false,
        interaction: { dragNodes: true, zoomView: true, dragView: true, hover: true },
      };
      if (mindmapNetworkRef.current) mindmapNetworkRef.current.destroy();
      const network = new Network(mindmapContainerRef.current, { nodes, edges }, options);
      // Big maps shrink to unreadable text when fitted; open on the root at a readable size instead
      network.once('afterDrawing', () => {
        if (network.getScale() < MIN_READABLE_SCALE) {
          const root = network.getPosition(1);
          const width = mindmapContainerRef.current?.clientWidth || 800;
          network.moveTo({
            position: { x: root.x + width / (2 * MIN_READABLE_SCALE) - 140, y: root.y },
            scale: MIN_READABLE_SCALE,
          });
        }
      });
      mindmapNetworkRef.current = network;
    }
  }, [mindmap, activeTab, busy.mindmap, theme]);

  // Render knowledge graph when data arrives
  useEffect(() => {
    if (knowledgeGraph && graphContainerRef.current && activeTab === 'graph') {
      const accent = token('--accent');
      const surface = token('--surface');
      const nodes = (knowledgeGraph.nodes || []).map((n) => ({
        id: n.id,
        label: n.label,
        shape: 'dot',
        size: 11,
        borderWidth: 3,
        color: {
          background: accent,
          border: token('--accent-soft'),
          highlight: { background: accent, border: accent },
          hover: { background: accent, border: accent },
        },
        font: { size: 14, face: FONT_FACE, color: token('--text'), strokeWidth: 4, strokeColor: surface },
      }));
      const edges = (knowledgeGraph.edges || []).map((e) => ({
        from: e.source,
        to: e.target,
        label: e.label || '',
        color: { color: token('--text-3'), opacity: 0.4, highlight: accent, hover: accent },
        width: 1.2,
        arrows: { to: { enabled: true, scaleFactor: 0.4 } },
        font: { size: 11, face: FONT_FACE, align: 'middle', color: token('--text-2'), strokeWidth: 4, strokeColor: surface },
        smooth: { type: 'continuous' },
      }));
      const options = {
        physics: {
          solver: 'forceAtlas2Based',
          forceAtlas2Based: { gravitationalConstant: -60, springLength: 160, avoidOverlap: 0.4 },
          stabilization: { iterations: 250 },
        },
        interaction: { hover: true, tooltipDelay: 200 },
      };
      if (graphNetworkRef.current) graphNetworkRef.current.destroy();
      const network = new Network(graphContainerRef.current, { nodes, edges }, options);
      network.once('stabilizationIterationsDone', () => network.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } }));
      graphNetworkRef.current = network;
    }
  }, [knowledgeGraph, activeTab, busy.graph, theme]);

  // Cleanup networks and audio on unmount
  useEffect(() => {
    return () => {
      if (mindmapNetworkRef.current) mindmapNetworkRef.current.destroy();
      if (graphNetworkRef.current) graphNetworkRef.current.destroy();
      if (audioRef.current) audioRef.current.pause();
    };
  }, []);

  const fetchDocumentInfo = async () => {
    try {
      const response = await axios.get(`/api/v1/document/${encodeURIComponent(docId)}`);
      setDocumentInfo(response.data);
    } catch (err) {
      setError('Couldn’t open this document: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleQuery = async (e, preset) => {
    if (e) e.preventDefault();
    const question = (preset ?? query).trim();
    if (!question || busy.query) return;

    // Earlier turns go along so follow-ups like "why?" or "tell me more" make sense
    const history = thread
      .filter((turn) => turn.answer)
      .flatMap((turn) => [
        { role: 'user', content: turn.question },
        { role: 'assistant', content: turn.answer },
      ]);

    setQuery('');
    setThread((current) => [...current, { question, answer: null }]);
    setTaskBusy('query', true);
    setError('');
    try {
      const response = await axios.post('/api/v1/query', { doc_id: docId, query: question, history });
      setThread((current) =>
        current.map((turn, i) => (i === current.length - 1 ? { ...turn, answer: response.data.response } : turn))
      );
    } catch (err) {
      setThread((current) => current.slice(0, -1));
      setQuery(question); // keep the question so it can be retried
      setError('Couldn’t answer that: ' + (err.response?.data?.detail || err.message));
    } finally {
      setTaskBusy('query', false);
    }
  };

  const startNewConversation = () => {
    if (audioRef.current) audioRef.current.pause();
    setSpeaking(null);
    setThread([]);
    setQuery('');
    askInputRef.current?.focus();
  };

  const handleSummarize = async () => {
    setTaskBusy('summary', true);
    setError('');
    setSummary('');
    try {
      const response = await axios.post('/api/v1/summarize', { doc_id: docId });
      setSummary(response.data.summary);
    } catch (err) {
      setError('Couldn’t write a summary: ' + (err.response?.data?.detail || err.message));
    } finally {
      setTaskBusy('summary', false);
    }
  };

  const handleExplain = async (e) => {
    e.preventDefault();
    if (!explanationText.trim()) return;
    setTaskBusy('explain', true);
    setError('');
    setExplanationResult('');
    try {
      const response = await axios.post('/api/v1/explain', { doc_id: docId, text: explanationText });
      setExplanationResult(response.data.explanation);
    } catch (err) {
      setError('Couldn’t explain that: ' + (err.response?.data?.detail || err.message));
    } finally {
      setTaskBusy('explain', false);
    }
  };

  const handleMindmap = async () => {
    setTaskBusy('mindmap', true);
    setError('');
    setMindmap(null);
    try {
      const response = await axios.get(`/api/v1/mindmap/${encodeURIComponent(docId)}`);
      setMindmap(response.data.mindmap);
    } catch (err) {
      setError('Couldn’t build the mindmap: ' + (err.response?.data?.detail || err.message));
    } finally {
      setTaskBusy('mindmap', false);
    }
  };

  const handleKnowledgeGraph = async () => {
    setTaskBusy('graph', true);
    setError('');
    setKnowledgeGraph(null);
    try {
      const response = await axios.get(`/api/v1/knowledge-graph/${encodeURIComponent(docId)}`);
      setKnowledgeGraph(response.data.knowledge_graph);
    } catch (err) {
      setError('Couldn’t build the knowledge graph: ' + (err.response?.data?.detail || err.message));
    } finally {
      setTaskBusy('graph', false);
    }
  };

  const handleTextToSpeech = async (text, key) => {
    if (audioRef.current) audioRef.current.pause();
    if (speaking === key) {
      setSpeaking(null);
      return;
    }
    setSpeaking(key);
    try {
      const response = await axios.post('/api/v1/tts', { doc_id: docId, text }, { responseType: 'blob' });
      const audioUrl = URL.createObjectURL(new Blob([response.data], { type: 'audio/wav' }));
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.onended = () => setSpeaking((current) => (current === key ? null : current));
      await audio.play();
    } catch (err) {
      setSpeaking(null);
      setError('Couldn’t play audio: ' + (err.response?.data?.detail || err.message));
    }
  };

  const openTab = (id) => {
    setActiveTab(id);
    if (id === 'summary' && !summary && !busy.summary) handleSummarize();
    if (id === 'mindmap' && !mindmap && !busy.mindmap) handleMindmap();
    if (id === 'graph' && !knowledgeGraph && !busy.graph) handleKnowledgeGraph();
  };

  const ListenButton = ({ text, id }) => (
    <button type="button" className="btn btn-ghost" onClick={() => handleTextToSpeech(text, id)}>
      {speaking === id ? <FiSquare size={14} /> : <FiVolume2 size={16} />}
      {speaking === id ? 'Stop' : 'Listen'}
    </button>
  );

  const FitButton = ({ networkRef }) => (
    <button
      type="button"
      className="btn btn-ghost"
      onClick={() => networkRef.current && networkRef.current.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } })}
    >
      <FiMaximize2 size={14} /> Fit to view
    </button>
  );

  if (!documentInfo) {
    return (
      <div className="viewer">
        <header className="viewer-header">
          <div className="skeleton" style={{ width: 90, height: 12 }} />
          <div className="skeleton" style={{ width: '55%', height: 40, marginTop: 14 }} />
        </header>
        {error && (
          <div className="notice notice-error fade">
            <FiAlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
      </div>
    );
  }

  const fileName = documentInfo.file_name || docId;
  const dot = fileName.lastIndexOf('.');
  const baseName = dot > 0 ? fileName.slice(0, dot) : fileName;
  const extension = dot > 0 ? fileName.slice(dot + 1).toUpperCase() : '';
  const sections = documentInfo.chunk_count;
  const previewSummary = summary || documentInfo.summary;

  return (
    <div className="viewer">
      <header className="viewer-header rise">
        <p className="eyebrow">Document</p>
        <h1 className="viewer-title">
          {baseName}
          {extension && <span className="ext-badge">{extension}</span>}
        </h1>
        <p className="viewer-meta">
          {sections} section{sections === 1 ? '' : 's'} · {Number(documentInfo.character_count).toLocaleString()} characters · Added{' '}
          {formatDate(documentInfo.processed_at)}
        </p>
      </header>

      <nav className="segmented rise rise-1" role="tablist" aria-label="Document tools">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            role="tab"
            aria-selected={activeTab === id}
            className={`segment ${activeTab === id ? 'is-active' : ''}`}
            onClick={() => openTab(id)}
          >
            <Icon size={15} />
            <span>{label}</span>
            {busy[id] && activeTab !== id && <span className="segment-dot" title="Working…" />}
          </button>
        ))}
      </nav>

      {error && (
        <div className="notice notice-error fade viewer-error">
          <FiAlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <section className="panel fade" key={activeTab}>
        {activeTab === 'info' && (
          <>
            <div className="stats">
              <div className="stat card">
                <span className="stat-value">{sections}</span>
                <span className="stat-label">Searchable section{sections === 1 ? '' : 's'}</span>
              </div>
              <div className="stat card">
                <span className="stat-value">{Number(documentInfo.character_count).toLocaleString()}</span>
                <span className="stat-label">Characters</span>
              </div>
              <div className="stat card">
                <span className="stat-value stat-value-sm">{formatDate(documentInfo.processed_at)}</span>
                <span className="stat-label">Added</span>
              </div>
            </div>

            <div className="card content-card">
              <p className="eyebrow">Summary</p>
              {previewSummary ? (
                <>
                  <p className="preview-text">{previewSummary.replace(/\*\*/g, '').slice(0, 280)}…</p>
                  <button className="btn btn-ghost card-action" onClick={() => openTab('summary')}>
                    Read the full summary
                  </button>
                </>
              ) : (
                <>
                  <p className="preview-text muted">No summary yet. It takes a few seconds to write one.</p>
                  <button className="btn btn-secondary btn-sm card-action" onClick={() => openTab('summary')}>
                    Summarize this document
                  </button>
                </>
              )}
            </div>

            <p className="fingerprint">
              Fingerprint <code>{documentInfo.hash?.slice(0, 16)}</code>
            </p>
          </>
        )}

        {activeTab === 'query' && (
          <>
            {thread.length > 0 && (
              <div className="thread" aria-live="polite">
                {thread.map((turn, i) => (
                  <div className="turn" key={i}>
                    <p className="bubble-question fade">{turn.question}</p>
                    {turn.answer === null ? (
                      <Thinking label="Looking through your document…" />
                    ) : (
                      <article className="card content-card fade">
                        <RichText text={turn.answer} />
                        <div className="card-actions">
                          <ListenButton text={turn.answer} id={`answer-${i}`} />
                        </div>
                      </article>
                    )}
                  </div>
                ))}
              </div>
            )}

            <form className="ask-bar card" onSubmit={handleQuery}>
              <FiMessageCircle size={20} className="ask-icon" />
              <input
                ref={askInputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={thread.length ? 'Ask a follow-up…' : 'Ask anything about this document'}
                disabled={busy.query}
                autoFocus
              />
              <button type="submit" className="ask-submit" disabled={busy.query || !query.trim()} aria-label="Ask">
                {busy.query ? <span className="spinner" /> : <FiArrowUp size={18} strokeWidth={2.6} />}
              </button>
            </form>

            {thread.length === 0 ? (
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button key={s} type="button" className="suggestion" onClick={() => handleQuery(null, s)}>
                    {s}
                  </button>
                ))}
              </div>
            ) : (
              <div className="thread-footer">
                <span className="muted small">
                  {thread.length} question{thread.length === 1 ? '' : 's'} · follow-ups remember this conversation
                </span>
                <button type="button" className="btn btn-ghost" onClick={startNewConversation} disabled={busy.query}>
                  <FiRotateCcw size={14} /> New conversation
                </button>
              </div>
            )}
            <div ref={threadEndRef} />
          </>
        )}

        {activeTab === 'summary' && (
          <>
            {busy.summary ? (
              <Thinking label="Writing a summary…" hint="The whole document is read, so long documents can take a few minutes." />
            ) : summary ? (
              <article className="card content-card reading">
                <RichText text={summary} />
                <div className="card-actions">
                  <ListenButton text={summary} id="summary" />
                </div>
              </article>
            ) : (
              <div className="empty">
                <p className="muted">Get the main points of this document in a few paragraphs.</p>
                <button className="btn btn-primary" onClick={handleSummarize}>
                  Summarize
                </button>
              </div>
            )}
          </>
        )}

        {activeTab === 'explain' && (
          <>
            <form className="card explain-form" onSubmit={handleExplain}>
              <textarea
                value={explanationText}
                onChange={(e) => setExplanationText(e.target.value)}
                placeholder="Paste a sentence or passage you’d like explained in plain language"
                rows="4"
                disabled={busy.explain}
              />
              <div className="explain-footer">
                <span className="muted small">{explanationText.trim() ? `${explanationText.trim().split(/\s+/).length} words` : ''}</span>
                <button type="submit" className="btn btn-primary btn-sm" disabled={busy.explain || !explanationText.trim()}>
                  {busy.explain ? (
                    <>
                      <span className="spinner" /> Explaining…
                    </>
                  ) : (
                    'Explain'
                  )}
                </button>
              </div>
            </form>

            {busy.explain && <Thinking label="Putting it in plain language…" />}

            {explanationResult && !busy.explain && (
              <article className="card content-card fade">
                <RichText text={explanationResult} />
                <div className="card-actions">
                  <ListenButton text={explanationResult} id="explanation" />
                </div>
              </article>
            )}
          </>
        )}

        {activeTab === 'mindmap' && (
          <>
            {busy.mindmap ? (
              <Thinking label="Mapping the main ideas…" hint="The whole document is read, so long documents can take a few minutes." />
            ) : mindmap ? (
              <div className="card canvas-card">
                <div className="canvas-toolbar">
                  <span className="muted small">Drag to move · Scroll to zoom</span>
                  <FitButton networkRef={mindmapNetworkRef} />
                </div>
                <div ref={mindmapContainerRef} className="vis-container" />
              </div>
            ) : (
              <div className="empty">
                <p className="muted">See the document’s topics and how they branch out.</p>
                <button className="btn btn-primary" onClick={handleMindmap}>
                  Create mindmap
                </button>
              </div>
            )}
          </>
        )}

        {activeTab === 'graph' && (
          <>
            {busy.graph ? (
              <Thinking label="Finding people, places and ideas…" hint="The whole document is read, so long documents can take a few minutes." />
            ) : knowledgeGraph ? (
              <div className="card canvas-card">
                <div className="canvas-toolbar">
                  <span className="muted small">
                    {(knowledgeGraph.nodes || []).length} concepts · {(knowledgeGraph.edges || []).length} connections
                  </span>
                  <FitButton networkRef={graphNetworkRef} />
                </div>
                <div ref={graphContainerRef} className="vis-container" />
              </div>
            ) : (
              <div className="empty">
                <p className="muted">See the key concepts in this document and how they connect.</p>
                <button className="btn btn-primary" onClick={handleKnowledgeGraph}>
                  Create graph
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
};

export default DocumentViewer;
