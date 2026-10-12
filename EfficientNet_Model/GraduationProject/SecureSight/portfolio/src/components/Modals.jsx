import React from 'react';
import { X, Download, Printer, ExternalLink, CheckCircle2, Shield, Sparkles, Cpu, Layers } from 'lucide-react';

export function ResumeModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadText = () => {
    const cvText = `
===================================================================
CURRICULUM VITAE - TASNEEM IBRAHIM
===================================================================
Email: tasneemibrahim.ai@gmail.com
LinkedIn: https://www.linkedin.com/in/tasneem-ibrahim-46a204331
Location: Egypt

PROFESSIONAL SUMMARY
AI Science student with strong foundations in Artificial Intelligence, Machine Learning, and software development. Focused on building intelligent systems and applying AI techniques to real-world problems, with hands-on experience in academic projects and Retrieval-Augmented Generation (RAG) systems.

EDUCATION
Alamein International University (AIU)
Bachelor of Science in Artificial Intelligence
- Expected Graduation: June 2026 (Final Academic Phase)
- Cumulative GPA: 3.2 / 4.0

EXPERIENCE
1. AI Research Assistant – RAG System Development (Ongoing Project)
   - Developed a Retrieval-Augmented Generation (RAG) AI web application.
   - Deployed and evaluated research retrieval workflows and vector search pipelines.

2. Information Technology Institute (ITI) – Field Training Program
   - 3-Month intensive software development training program.
   - Built complete desktop software application with structured SDLC architecture.

TECHNICAL SKILLS
- Programming Languages: Python, Java, JavaScript, R, SQL
- AI & Machine Learning: PyTorch, TensorFlow, Keras, scikit-learn, OpenCV, NumPy, Pandas, Matplotlib, Plotly
- Web Development: React, Node.js, Express.js, HTML5, CSS3, JavaScript
- Databases: MongoDB, MySQL
- Cloud & MLOps: AWS, Docker, Kubernetes, Apache Kafka
- Tools: Git, GitHub, Postman, JWT Authentication
- Embedded & Hardware: Raspberry Pi, Jetson Nano

CERTIFICATIONS
- Information Technology Institute (ITI) Field Training Certificate
- CCNA (Cisco Certified Network Associate)
- Coursera & Maharatech AI/Software Certificates
`;
    const blob = new Blob([cvText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Tasneem_Ibrahim_CV.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 200,
        background: 'rgba(5, 8, 15, 0.85)',
        backdropFilter: 'blur(16px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem'
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '850px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-glow)'
        }}
      >
        {/* Top Header */}
        <div
          style={{
            padding: '1.25rem 1.75rem',
            borderBottom: '1px solid var(--border-glass)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'var(--bg-card)'
          }}
        >
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
              Curriculum Vitae – <span className="text-gradient">Tasneem Ibrahim</span>
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
              AI Engineer & Full-Stack Developer
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button onClick={handleDownloadText} className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.82rem' }}>
              <Download size={15} />
              <span>Download CV</span>
            </button>
            <button onClick={handlePrint} className="btn-secondary" style={{ padding: '0.5rem', fontSize: '0.82rem' }} title="Print CV">
              <Printer size={16} />
            </button>
            <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '0.4rem' }}>
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Scrollable CV Document View */}
        <div style={{ padding: '2rem', overflowY: 'auto', flex: 1, fontSize: '0.94rem', lineHeight: 1.7 }}>
          
          {/* Header Contact Block */}
          <div style={{ paddingBottom: '1.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
              TASNEEM IBRAHIM
            </h2>
            <div style={{ color: 'var(--accent-cyan)', fontWeight: 600, fontSize: '1rem', marginBottom: '0.75rem' }}>
              Artificial Intelligence Engineer | RAG Systems & Full-Stack Developer
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.86rem', color: 'var(--text-muted)' }}>
              <span>Email: <strong style={{ color: 'var(--text-main)' }}>tasneemibrahim.ai@gmail.com</strong></span>
              <span>•</span>
              <span>LinkedIn: <strong style={{ color: 'var(--accent-indigo)' }}>linkedin.com/in/tasneem-ibrahim-46a204331</strong></span>
              <span>•</span>
              <span>Location: <strong>Egypt</strong></span>
            </div>
          </div>

          {/* Section: Professional Summary */}
          <div style={{ marginBottom: '1.75rem' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-cyan)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Professional Summary
            </h4>
            <p style={{ color: 'var(--text-muted)' }}>
              AI Science student at Alamein International University with strong foundations in Artificial Intelligence, Machine Learning, and modern software development. Focused on building intelligent systems and applying AI techniques to real-world problems, with hands-on experience in research projects and Retrieval-Augmented Generation (RAG) platforms.
            </p>
          </div>

          {/* Section: Education */}
          <div style={{ marginBottom: '1.75rem' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-cyan)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Education
            </h4>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: 'var(--text-main)' }}>
                <span>Alamein International University (AIU)</span>
                <span>Expected Graduation: June 2026</span>
              </div>
              <div style={{ color: 'var(--accent-purple)', fontWeight: 600, fontSize: '0.9rem' }}>
                Bachelor of Science in Artificial Intelligence — GPA: 3.2 / 4.0
              </div>
              <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>Current Academic Status: Final Phase (May 2026)</div>
            </div>
          </div>

          {/* Section: Experience */}
          <div style={{ marginBottom: '1.75rem' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-cyan)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Experience & Projects
            </h4>
            
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: 'var(--text-main)' }}>
                <span>AI Research Assistant – RAG System Development</span>
                <span style={{ color: 'var(--accent-cyan)' }}>2025 – Present</span>
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
                Developed a Retrieval-Augmented Generation (RAG) AI web application for academic research document search and literature synthesis. System deployed and currently under testing and evaluation.
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: 'var(--text-main)' }}>
                <span>Information Technology Institute (ITI) – Field Training Program</span>
                <span style={{ color: 'var(--accent-purple)' }}>3 Months</span>
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
                3-month intensive software development training program. Built a desktop application project as part of training, gaining structured programming and software engineering fundamentals.
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: 'var(--text-main)' }}>
                <span>SecureSight – EfficientNet AI Computer Vision System</span>
                <span style={{ color: 'var(--accent-emerald)' }}>Graduation Project</span>
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
                Engineered an EfficientNet deep learning computer vision model for automated visual detection, feature extraction, and security diagnostics.
              </div>
            </div>
          </div>

          {/* Section: Technical Skills */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-cyan)', marginBottom: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Technical Skills
            </h4>
            <ul style={{ paddingLeft: '1.2rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              <li><strong>Programming:</strong> Python, Java, JavaScript, R, SQL</li>
              <li><strong>AI & ML:</strong> PyTorch, TensorFlow, Keras, scikit-learn, OpenCV, RAG, NumPy, Pandas, Matplotlib, Plotly</li>
              <li><strong>Web Dev:</strong> React, Node.js, Express.js, HTML5, CSS3, REST APIs</li>
              <li><strong>Databases & Cloud:</strong> MongoDB, MySQL, AWS, Docker, Kubernetes, Apache Kafka, Git, Postman</li>
              <li><strong>Hardware:</strong> Raspberry Pi, Jetson Nano</li>
            </ul>
          </div>

        </div>
      </div>
    </div>
  );
}

export function ProjectModal({ project, onClose }) {
  if (!project) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 200,
        background: 'rgba(5, 8, 15, 0.85)',
        backdropFilter: 'blur(16px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem'
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '700px',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: '2rem',
          position: 'relative',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-glow)'
        }}
      >
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={24} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border-glass)' }}>
            {project.icon}
          </div>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
              {project.categoryLabel}
            </span>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', lineHeight: 1.2 }}>
              {project.title}
            </h3>
          </div>
        </div>

        <div style={{ margin: '1.5rem 0', padding: '1.25rem', borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-glass)' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            System Overview & Architecture
          </h4>
          <p style={{ fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            {project.details}
          </p>
        </div>

        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem' }}>
          Technologies Used
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.75rem' }}>
          {project.tags.map((t, i) => (
            <span key={i} className="badge-glow" style={{ fontSize: '0.8rem' }}>
              {t}
            </span>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          {project.id === 'rag-assistant' ? (
            <a href="#rag-lab" onClick={onClose} className="btn-primary" style={{ flex: 1, padding: '0.75rem' }}>
              <Sparkles size={16} />
              <span>Launch Interactive RAG Simulator</span>
            </a>
          ) : (
            <button onClick={onClose} className="btn-primary" style={{ flex: 1, padding: '0.75rem' }}>
              <CheckCircle2 size={16} />
              <span>Close View</span>
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
