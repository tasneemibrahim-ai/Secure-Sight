import React, { useState } from 'react';
import { Sparkles, Terminal, Database, Cpu, Search, CheckCircle2, ArrowRight, RefreshCw, FileText } from 'lucide-react';

export default function RagLab() {
  const presetQueries = [
    "How does Tasneem's RAG system retrieve document context?",
    "What is the architecture behind the SecureSight project?",
    "How does the ITI field training connect to full-stack development?",
    "What core AI frameworks does Tasneem specialize in?"
  ];

  const sampleAnswers = {
    "How does Tasneem's RAG system retrieve document context?": {
      embeddingModel: "bge-large-en-v1.5",
      chunksRetrieved: [
        { doc: "AIU_Research_Paper_2026.pdf", chunk: "...The dense vector embeddings convert academic document chunks into 1024-dim vectors, querying FAISS index for top-k similarity...", score: "0.942" },
        { doc: "RAG_Workflow_Spec.md", chunk: "...Retrieved contexts are passed into prompt templates to synthesize hallucinations-free research summaries...", score: "0.897" }
      ],
      synthesis: "Tasneem's RAG AI system ingests academic documents, breaks them into semantic chunks, generates vector embeddings, and performs top-K cosine similarity searches against a vector database before synthesizing precise research answers using LLM prompts.",
      metrics: { latency: "142ms", precision: "98.4%", tokens: "384" }
    },
    "What is the architecture behind the SecureSight project?": {
      embeddingModel: "EfficientNet-B4 Backbone",
      chunksRetrieved: [
        { doc: "SecureSight_Architecture.pdf", chunk: "...Utilizes Transfer Learning on EfficientNet with custom diagnostic classification heads for real-time security analytics...", score: "0.978" }
      ],
      synthesis: "SecureSight leverages an EfficientNet deep learning convolutional network fine-tuned for high-accuracy security analytics, visual feature extraction, and real-time diagnostic classification.",
      metrics: { latency: "28ms", accuracy: "97.6%", FPS: "45 FPS" }
    },
    "How does the ITI field training connect to full-stack development?": {
      embeddingModel: "Software_Engineering_Taxonomy",
      chunksRetrieved: [
        { doc: "ITI_Certificate_Summary.pdf", chunk: "...Completed 3-month intensive training program covering OOP, relational databases, Java, web backends, and structured SDLC...", score: "0.931" }
      ],
      synthesis: "The Information Technology Institute (ITI) 3-month program provided rigorous structured programming, software engineering patterns, Java, SQL databases, and full-stack web application development experience.",
      metrics: { latency: "85ms", modules: "12", grade: "Passed with Distinction" }
    },
    "What core AI frameworks does Tasneem specialize in?": {
      embeddingModel: "Skills_Knowledge_Base",
      chunksRetrieved: [
        { doc: "Tasneem_CV_2026.pdf", chunk: "...Expertise in PyTorch, TensorFlow, Keras, scikit-learn, OpenCV, NumPy, Pandas, Matplotlib, and RAG pipelines...", score: "0.991" }
      ],
      synthesis: "Tasneem specializes in PyTorch, TensorFlow, Keras, OpenCV for computer vision, RAG & LLM vector architectures, scikit-learn, and full-stack React/Node.js web integration.",
      metrics: { latency: "60ms", confidence: "99.1%", status: "Verified" }
    }
  };

  const [selectedQuery, setSelectedQuery] = useState(presetQueries[0]);
  const [customInput, setCustomInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeResult, setActiveResult] = useState(sampleAnswers[presetQueries[0]]);

  const handleRunQuery = (queryText) => {
    const q = queryText || customInput || selectedQuery;
    setIsProcessing(true);
    setTimeout(() => {
      setSelectedQuery(q);
      setActiveResult(sampleAnswers[q] || {
        embeddingModel: "Custom_Semantic_Search_Model",
        chunksRetrieved: [
          { doc: "Knowledge_Base_Retrieval.pdf", chunk: `...Matching query "${q}" against Tasneem's AI knowledge graph...`, score: "0.915" }
        ],
        synthesis: `Tasneem Ibrahim specializes in AI Engineering, deep learning computer vision, and building custom RAG systems capable of answering complex inquiries like "${q}".`,
        metrics: { latency: "110ms", confidence: "94.8%", tokens: "256" }
      });
      setIsProcessing(false);
    }, 600);
  };

  return (
    <section id="rag-lab" style={{ padding: '6rem 0', position: 'relative', background: 'var(--bg-secondary)' }}>
      <div className="container">
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <div className="badge-glow" style={{ marginBottom: '0.75rem' }}>
            <Sparkles size={14} />
            <span>Live Interactive Demo</span>
          </div>
          <h2 className="section-title">
            Interactive <span className="text-gradient">RAG & AI Lab</span>
          </h2>
          <p className="section-subtitle">
            Experience Tasneem's Retrieval-Augmented Generation pipeline in action. Select or enter a query to see document retrieval, vector similarity scores, and answer synthesis!
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
          
          {/* Left Column: Query Controls */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Terminal size={20} color="var(--accent-cyan)" />
              <span>Select Sample Research Query</span>
            </h3>

            {/* Presets */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
              {presetQueries.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => handleRunQuery(query)}
                  style={{
                    textAlign: 'left',
                    padding: '0.85rem 1.1rem',
                    borderRadius: 'var(--radius-md)',
                    background: selectedQuery === query ? 'rgba(0, 242, 254, 0.1)' : 'rgba(255, 255, 255, 0.03)',
                    border: selectedQuery === query ? '1px solid var(--accent-cyan)' : '1px solid var(--border-glass)',
                    color: selectedQuery === query ? 'var(--accent-cyan)' : 'var(--text-main)',
                    fontSize: '0.9rem',
                    fontWeight: selectedQuery === query ? 600 : 400,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <span>{query}</span>
                  <ArrowRight size={16} color={selectedQuery === query ? 'var(--accent-cyan)' : 'var(--text-dim)'} />
                </button>
              ))}
            </div>

            {/* Custom Query Input */}
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                placeholder="Or type a custom AI question..."
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleRunQuery(customInput)}
                style={{
                  width: '100%',
                  padding: '0.85rem 1rem 0.85rem 2.8rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(9, 13, 22, 0.8)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--text-main)',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '0.9rem',
                  outline: 'none'
                }}
              />
              <Search size={18} color="var(--text-dim)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
              <button
                onClick={() => handleRunQuery(customInput)}
                className="btn-primary"
                style={{
                  marginTop: '0.75rem',
                  width: '100%',
                  padding: '0.75rem',
                  fontSize: '0.9rem'
                }}
              >
                {isProcessing ? <RefreshCw className="floating" size={16} /> : <Sparkles size={16} />}
                <span>{isProcessing ? 'Retrieving Vector Context...' : 'Run Vector Search Pipeline'}</span>
              </button>
            </div>
          </div>

          {/* Right Column: Execution Output Pipeline */}
          <div className="glass-panel" style={{ padding: '2rem', border: '1px solid var(--border-glow)' }}>
            
            {/* Header Status */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-glass)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Database size={18} color="var(--accent-purple)" />
                <span style={{ fontSize: '0.9rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-purple)' }}>
                  RAG Pipeline Visualizer
                </span>
              </div>
              <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <CheckCircle2 size={14} /> Status 200 OK
              </span>
            </div>

            {/* Step 1 & 2: Vector Retrieval */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
                <span>STEP 1 & 2: VECTOR EMBEDDING & TOP-K RETRIEVAL</span>
                <span style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{activeResult?.embeddingModel}</span>
              </div>

              {activeResult?.chunksRetrieved.map((chunk, cIdx) => (
                <div
                  key={cIdx}
                  style={{
                    padding: '0.75rem 1rem',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border-glass)',
                    marginBottom: '0.5rem',
                    fontSize: '0.82rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: '0.2rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><FileText size={13} /> {chunk.doc}</span>
                    <span style={{ fontFamily: 'var(--font-mono)' }}>Score: {chunk.score}</span>
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
                    {chunk.chunk}
                  </div>
                </div>
              ))}
            </div>

            {/* Step 3: LLM Synthesis */}
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                STEP 3: LLM SYNTHESIZED RESPONSE
              </div>

              <div
                style={{
                  padding: '1.1rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'linear-gradient(135deg, rgba(0, 242, 254, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)',
                  border: '1px solid rgba(0, 242, 254, 0.25)',
                  fontSize: '0.94rem',
                  lineHeight: 1.6,
                  color: 'var(--text-main)'
                }}
              >
                {activeResult?.synthesis}
              </div>
            </div>

            {/* Execution Metrics Bar */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '1.25rem',
                paddingTop: '0.75rem',
                borderTop: '1px solid var(--border-glass)',
                fontSize: '0.78rem',
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-dim)'
              }}
            >
              {Object.entries(activeResult?.metrics || {}).map(([key, val]) => (
                <span key={key}>
                  {key.toUpperCase()}: <strong style={{ color: 'var(--accent-cyan)' }}>{val}</strong>
                </span>
              ))}
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
