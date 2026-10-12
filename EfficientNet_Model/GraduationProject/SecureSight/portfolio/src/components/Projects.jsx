import React, { useState } from 'react';
import { Code2, ExternalLink, Github, Sparkles, Shield, Cpu, Layers, Eye } from 'lucide-react';

export default function Projects({ onSelectProject }) {
  const [activeFilter, setActiveFilter] = useState('all');

  const projects = [
    {
      id: 'securesight',
      title: 'SecureSight – EfficientNet AI Computer Vision System',
      category: 'vision',
      categoryLabel: 'AI & Computer Vision (Graduation Project)',
      summary: 'State-of-the-art Deep Learning Computer Vision architecture utilizing EfficientNet for high-accuracy security analytics, automated visual detection, and feature extraction.',
      details: 'SecureSight is an advanced AI computer vision system designed for real-time visual detection and security diagnostics. Built using EfficientNet backbones with transfer learning, custom loss functions, and OpenCV image preprocessing. Achieves state-of-the-art classification accuracy with optimized model latency for edge deployment.',
      tags: ['PyTorch', 'EfficientNet', 'OpenCV', 'Computer Vision', 'Python', 'CUDA', 'Flask API'],
      featured: true,
      icon: <Shield size={24} color="var(--accent-cyan)" />,
      badge: 'Graduation Project'
    },
    {
      id: 'rag-assistant',
      title: 'Academic RAG AI Research Assistant System',
      category: 'rag',
      categoryLabel: 'RAG & LLM Systems',
      summary: 'Retrieval-Augmented Generation (RAG) platform deployed to enhance academic research workflows by retrieving relevant literature context and synthesizing accurate AI answers.',
      details: 'Designed and deployed an end-to-end RAG AI web application. Features custom document chunking, dense vector embeddings, vector database similarity search, and LLM prompt engineering to eliminate hallucinations and accelerate scientific literature synthesis.',
      tags: ['RAG', 'PyTorch', 'Vector DB', 'Embeddings', 'React', 'Express.js', 'Python'],
      featured: true,
      icon: <Sparkles size={24} color="var(--accent-purple)" />,
      badge: 'Ongoing AI Research'
    },
    {
      id: 'iti-desktop',
      title: 'ITI Field Training Desktop Application',
      category: 'software',
      categoryLabel: 'Software Engineering',
      summary: 'Enterprise-level structured desktop software application engineered during the 3-Month Intensive Software Training Program at Information Technology Institute (ITI).',
      details: 'Built as the capstone project during ITI training. Designed clean object-oriented architecture, relational database persistence, modular UI components, and strict error handling.',
      tags: ['Java', 'SQL', 'Desktop GUI', 'Software Engineering', 'Git', 'ITI Project'],
      featured: false,
      icon: <Code2 size={24} color="var(--accent-emerald)" />,
      badge: 'ITI Certified'
    },
    {
      id: 'smart-home-iot',
      title: 'Smart Home IoT Automation & Packet Tracer System',
      category: 'software',
      categoryLabel: 'IoT & Networking',
      summary: 'Integrated IoT hardware and simulated smart home automation network combining Cisco Packet Tracer, Raspberry Pi, and embedded sensor control logic.',
      details: 'Implemented smart home automation with networked sensors, central controller scripts, and real-time monitoring. Integrated hardware components with Raspberry Pi and Jetson Nano modules.',
      tags: ['Raspberry Pi', 'Cisco Packet Tracer', 'IoT', 'Python', 'Networking'],
      featured: false,
      icon: <Cpu size={24} color="var(--accent-cyan)" />,
      badge: 'IoT Systems'
    },
    {
      id: 'digit-recognizer',
      title: 'Deep Learning Handwritten Digit Recognizer',
      category: 'vision',
      categoryLabel: 'Deep Learning',
      summary: 'Neural network vision model trained on MNIST handwritten digit recognition dataset using PyTorch, achieving over 98% validation accuracy.',
      details: 'Implemented multi-layer Convolutional Neural Networks (CNN) with custom hyperparameter tuning, confusion matrix evaluation, and interactive drawing canvas predictor.',
      tags: ['PyTorch', 'CNN', 'Jupyter Notebook', 'Matplotlib', 'Scikit-learn'],
      featured: false,
      icon: <Eye size={24} color="var(--accent-purple)" />,
      badge: 'ML Project'
    }
  ];

  const filters = [
    { id: 'all', label: 'All Projects' },
    { id: 'vision', label: 'Computer Vision' },
    { id: 'rag', label: 'RAG & AI Systems' },
    { id: 'software', label: 'Software & IoT' },
  ];

  const filteredProjects = activeFilter === 'all'
    ? projects
    : projects.filter(p => p.category === activeFilter);

  return (
    <section id="projects" style={{ padding: '6rem 0', position: 'relative' }}>
      <div className="container">
        
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <div className="badge-glow" style={{ marginBottom: '0.75rem' }}>
            <Layers size={14} />
            <span>Featured Portfolio Work</span>
          </div>
          <h2 className="section-title">
            Key <span className="text-gradient">Projects & Systems</span>
          </h2>
          <p className="section-subtitle">
            A selection of AI models, RAG architectures, full-stack web applications, and embedded hardware projects engineered by Tasneem.
          </p>
        </div>

        {/* Filter Buttons */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '0.75rem',
            marginBottom: '3rem',
            flexWrap: 'wrap'
          }}
        >
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.id)}
              style={{
                padding: '0.6rem 1.25rem',
                borderRadius: '9999px',
                background: activeFilter === f.id ? 'var(--grad-cyan-blue)' : 'var(--bg-card)',
                color: activeFilter === f.id ? '#000' : 'var(--text-muted)',
                border: activeFilter === f.id ? 'none' : '1px solid var(--border-glass)',
                fontWeight: activeFilter === f.id ? 700 : 500,
                fontSize: '0.88rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Project Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '2rem'
          }}
        >
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="glass-panel"
              style={{
                padding: '2rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                border: project.featured ? '1px solid rgba(0, 242, 254, 0.35)' : '1px solid var(--border-glass)'
              }}
            >
              <div>
                {/* Header Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                  <div
                    style={{
                      width: '46px',
                      height: '46px',
                      borderRadius: '12px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid var(--border-glass)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {project.icon}
                  </div>
                  <span
                    className="badge-glow"
                    style={{
                      fontSize: '0.72rem',
                      padding: '0.25rem 0.65rem'
                    }}
                  >
                    {project.badge}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.6rem', lineHeight: 1.3 }}>
                  {project.title}
                </h3>

                <p style={{ fontSize: '0.93rem', color: 'var(--text-muted)', lineHeight: 1.65, marginBottom: '1.5rem' }}>
                  {project.summary}
                </p>

                {/* Tech Tags */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1.75rem' }}>
                  {project.tags.map((tag, tIdx) => (
                    <span
                      key={tIdx}
                      style={{
                        fontSize: '0.75rem',
                        fontFamily: 'var(--font-mono)',
                        padding: '0.25rem 0.55rem',
                        borderRadius: '6px',
                        background: 'rgba(255, 255, 255, 0.04)',
                        color: 'var(--text-main)',
                        border: '1px solid var(--border-glass)'
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Links */}
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
                <button
                  onClick={() => onSelectProject(project)}
                  className="btn-secondary"
                  style={{ flex: 1, padding: '0.6rem 1rem', fontSize: '0.85rem' }}
                >
                  View System Architecture
                </button>
                {project.id === 'rag-assistant' && (
                  <a
                    href="#rag-lab"
                    className="btn-primary"
                    style={{ padding: '0.6rem 1rem', fontSize: '0.85rem' }}
                  >
                    <Sparkles size={14} />
                    <span>Live Demo</span>
                  </a>
                )}
              </div>

            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
