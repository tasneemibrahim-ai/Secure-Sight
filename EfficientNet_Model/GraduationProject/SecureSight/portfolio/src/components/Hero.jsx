import React, { useState, useEffect } from 'react';
import { ArrowRight, Sparkles, Terminal, Code2, Brain, Database, ShieldCheck, Mail } from 'lucide-react';

export default function Hero({ onOpenContact }) {
  const roles = [
    'AI & Machine Learning Engineer',
    'RAG & LLM Systems Researcher',
    'Computer Vision Specialist (SecureSight)',
    'Full-Stack Software Developer'
  ];

  const [roleIndex, setRoleIndex] = useState(0);
  const [displayText, setDisplayText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentRole = roles[roleIndex];
    let typingSpeed = isDeleting ? 40 : 80;

    if (!isDeleting && displayText === currentRole) {
      typingSpeed = 2200; // Pause at end
      setIsDeleting(true);
    } else if (isDeleting && displayText === '') {
      setIsDeleting(false);
      setRoleIndex((prev) => (prev + 1) % roles.length);
      typingSpeed = 400;
    }

    const timer = setTimeout(() => {
      setDisplayText(
        isDeleting
          ? currentRole.substring(0, displayText.length - 1)
          : currentRole.substring(0, displayText.length + 1)
      );
    }, typingSpeed);

    return () => clearTimeout(timer);
  }, [displayText, isDeleting, roleIndex]);

  return (
    <section
      id="hero"
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        position: 'relative',
        paddingTop: '6rem',
        paddingBottom: '4rem',
        overflow: 'hidden'
      }}
    >
      {/* Background glow ornaments */}
      <div className="ambient-glow glow-1" />
      <div className="ambient-glow glow-2" />

      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '3rem',
            alignItems: 'center'
          }}
        >
          {/* Left Column - Text Content */}
          <div>
            <div className="badge-glow" style={{ marginBottom: '1.5rem' }}>
              <span className="badge-dot" />
              <span>Available for AI & Software Roles</span>
            </div>

            <h1
              style={{
                fontSize: 'clamp(2.5rem, 5vw, 3.8rem)',
                fontWeight: 800,
                lineHeight: 1.15,
                letterSpacing: '-0.03em',
                marginBottom: '1.25rem'
              }}
            >
              Hi, I'm <span className="text-gradient">Tasneem Ibrahim</span>
            </h1>

            {/* Typewriter Subtitle */}
            <div
              style={{
                fontSize: 'clamp(1.15rem, 2.5vw, 1.5rem)',
                fontWeight: 600,
                color: 'var(--accent-cyan)',
                fontFamily: 'var(--font-mono)',
                minHeight: '2.4rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                marginBottom: '1.5rem'
              }}
            >
              <Terminal size={22} color="var(--accent-cyan)" />
              <span>{displayText}</span>
              <span style={{ animation: 'pulse-dot 0.8s infinite', color: 'var(--accent-cyan)' }}>|</span>
            </div>

            <p
              style={{
                fontSize: '1.1rem',
                color: 'var(--text-muted)',
                lineHeight: 1.7,
                marginBottom: '2.2rem',
                maxWidth: '560px'
              }}
            >
              AI Science student at <strong>Alamein International University (AIU)</strong>. Specializing in 
              building intelligent Retrieval-Augmented Generation (RAG) platforms, deep learning computer vision architectures 
              (<em>SecureSight</em>), and modern scalable full-stack applications.
            </p>

            {/* CTA Action Buttons */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
              <a href="#rag-lab" className="btn-primary">
                <Sparkles size={18} />
                <span>Test RAG Lab</span>
                <ArrowRight size={18} />
              </a>

              <a href="#projects" className="btn-secondary">
                <Code2 size={18} />
                <span>View Projects</span>
              </a>

              <button onClick={onOpenContact} className="btn-secondary" style={{ borderColor: 'var(--accent-purple)', color: 'var(--accent-purple)' }}>
                <Mail size={18} />
                <span>Contact Me</span>
              </button>
            </div>

            {/* Quick Metrics Bar */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '1.25rem',
                marginTop: '3rem',
                paddingTop: '2rem',
                borderTop: '1px solid var(--border-glass)'
              }}
            >
              <div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                  3.2 / 4.0
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>AIU GPA</div>
              </div>

              <div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-purple)', fontFamily: 'var(--font-mono)' }}>
                  RAG & CV
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>AI Specialization</div>
              </div>

              <div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-emerald)', fontFamily: 'var(--font-mono)' }}>
                  ITI 3-Mo
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Software Training</div>
              </div>
            </div>
          </div>

          {/* Right Column - Visual Interactive Card / Avatar Graphic */}
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div
              className="glass-panel floating"
              style={{
                width: '100%',
                maxWidth: '440px',
                padding: '2rem',
                position: 'relative',
                background: 'linear-gradient(145deg, rgba(18, 24, 38, 0.9) 0%, rgba(10, 14, 23, 0.95) 100%)',
                border: '1px solid var(--border-glow)'
              }}
            >
              {/* Card Top Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '0.4rem' }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff5f56' }} />
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ffbd2e' }} />
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#27c93f' }} />
                </div>
                <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                  tasneem_ai_core.py
                </span>
              </div>

              {/* Code Snippet / Visual Dashboard */}
              <div className="code-block" style={{ marginBottom: '1.5rem', fontSize: '0.82rem' }}>
                <div style={{ color: 'var(--text-dim)' }}># AI Research Assistant Pipeline</div>
                <div><span style={{ color: '#ec4899' }}>from</span> rag_engine <span style={{ color: '#ec4899' }}>import</span> VectorStore, LLMSynthesizer</div>
                <div><span style={{ color: '#ec4899' }}>from</span> vision <span style={{ color: '#ec4899' }}>import</span> EfficientNet</div>
                <br />
                <div><span style={{ color: '#00f2fe' }}>class</span> <span style={{ color: '#facc15' }}>TasneemAI</span>:</div>
                <div style={{ paddingLeft: '1.2rem' }}>degree = <span style={{ color: '#a855f7' }}>"B.Sc. AI (AIU)"</span></div>
                <div style={{ paddingLeft: '1.2rem' }}>status = <span style={{ color: '#10b981' }}>"Ready for AI & Dev roles"</span></div>
                <div style={{ paddingLeft: '1.2rem' }}>skills = [<span style={{ color: '#00f2fe' }}>"PyTorch"</span>, <span style={{ color: '#00f2fe' }}>"RAG"</span>, <span style={{ color: '#00f2fe' }}>"React"</span>, <span style={{ color: '#00f2fe' }}>"Docker"</span>]</div>
              </div>

              {/* Core Skill Chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                <span className="badge-glow" style={{ fontSize: '0.75rem', padding: '0.3rem 0.7rem' }}>
                  <Brain size={12} /> PyTorch & ML
                </span>
                <span className="badge-glow" style={{ fontSize: '0.75rem', padding: '0.3rem 0.7rem', borderColor: 'rgba(168, 85, 247, 0.3)', color: 'var(--accent-purple)' }}>
                  <Database size={12} /> RAG & Embeddings
                </span>
                <span className="badge-glow" style={{ fontSize: '0.75rem', padding: '0.3rem 0.7rem', borderColor: 'rgba(16, 185, 129, 0.3)', color: 'var(--accent-emerald)' }}>
                  <ShieldCheck size={12} /> SecureSight CV
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
