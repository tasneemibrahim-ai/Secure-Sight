import React, { useState } from 'react';
import { Cpu, Code2, Server, HardDrive, Terminal, CheckCircle } from 'lucide-react';

export default function Skills() {
  const [activeTab, setActiveTab] = useState('all');

  const categories = [
    { id: 'all', name: 'All Skills', icon: <Terminal size={16} /> },
    { id: 'ai', name: 'AI & Machine Learning', icon: <Cpu size={16} /> },
    { id: 'web', name: 'Web & Software', icon: <Code2 size={16} /> },
    { id: 'cloud', name: 'Cloud, MLOps & DevOps', icon: <Server size={16} /> },
    { id: 'hardware', name: 'Embedded & Tools', icon: <HardDrive size={16} /> },
  ];

  const skillList = [
    // AI & ML
    { name: 'PyTorch', category: 'ai', level: 92, tag: 'Deep Learning' },
    { name: 'TensorFlow / Keras', category: 'ai', level: 88, tag: 'Neural Networks' },
    { name: 'RAG & Vector DBs', category: 'ai', level: 95, tag: 'LLM Systems' },
    { name: 'OpenCV', category: 'ai', level: 85, tag: 'Computer Vision' },
    { name: 'scikit-learn', category: 'ai', level: 90, tag: 'ML Algorithms' },
    { name: 'NumPy & Pandas', category: 'ai', level: 95, tag: 'Data Engineering' },
    { name: 'Matplotlib & Plotly', category: 'ai', level: 88, tag: 'Data Visualization' },

    // Web & Software
    { name: 'Python', category: 'web', level: 96, tag: 'Core Language' },
    { name: 'JavaScript / Node.js', category: 'web', level: 90, tag: 'Full-Stack' },
    { name: 'React.js', category: 'web', level: 88, tag: 'Frontend' },
    { name: 'Express.js', category: 'web', level: 86, tag: 'Backend APIs' },
    { name: 'Java', category: 'web', level: 85, tag: 'OOP & Software' },
    { name: 'R', category: 'web', level: 80, tag: 'Data Analysis' },
    { name: 'SQL & MySQL', category: 'web', level: 88, tag: 'Relational DB' },
    { name: 'MongoDB', category: 'web', level: 85, tag: 'NoSQL' },

    // Cloud & DevOps
    { name: 'Docker', category: 'cloud', level: 85, tag: 'Containerization' },
    { name: 'AWS', category: 'cloud', level: 80, tag: 'Cloud Infrastructure' },
    { name: 'Kubernetes', category: 'cloud', level: 75, tag: 'Orchestration' },
    { name: 'Apache Kafka', category: 'cloud', level: 78, tag: 'Event Streaming' },
    { name: 'Git & GitHub', category: 'cloud', level: 92, tag: 'Version Control' },
    { name: 'Postman & REST APIs', category: 'cloud', level: 90, tag: 'API Testing' },
    { name: 'JWT & Security', category: 'cloud', level: 85, tag: 'Auth Security' },

    // Hardware & Embedded
    { name: 'Jetson Nano', category: 'hardware', level: 84, tag: 'Edge AI' },
    { name: 'Raspberry Pi', category: 'hardware', level: 88, tag: 'IoT Embedded' },
  ];

  const filteredSkills = activeTab === 'all'
    ? skillList
    : skillList.filter(s => s.category === activeTab);

  return (
    <section id="skills" style={{ padding: '6rem 0', position: 'relative' }}>
      <div className="container">
        
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <div className="badge-glow" style={{ marginBottom: '0.75rem' }}>
            <Cpu size={14} />
            <span>Technical Capabilities</span>
          </div>
          <h2 className="section-title">
            Skills & <span className="text-gradient">Tech Stack</span>
          </h2>
          <p className="section-subtitle">
            Comprehensive skill set spanning artificial intelligence, neural networks, full-stack software development, and cloud infrastructure.
          </p>
        </div>

        {/* Filter Tabs */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            flexWrap: 'wrap',
            gap: '0.75rem',
            marginBottom: '3rem'
          }}
        >
          {categories.map((cat) => {
            const isActive = activeTab === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setActiveTab(cat.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.65rem 1.25rem',
                  borderRadius: '9999px',
                  background: isActive ? 'var(--grad-cyber)' : 'var(--bg-card)',
                  color: isActive ? '#000' : 'var(--text-muted)',
                  border: isActive ? 'none' : '1px solid var(--border-glass)',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  transition: 'all 0.25s ease',
                  boxShadow: isActive ? '0 0 20px rgba(0, 242, 254, 0.35)' : 'none'
                }}
              >
                {cat.icon}
                <span>{cat.name}</span>
              </button>
            );
          })}
        </div>

        {/* Skills Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '1.25rem'
          }}
        >
          {filteredSkills.map((skill, idx) => (
            <div
              key={idx}
              className="glass-panel"
              style={{
                padding: '1.25rem 1.5rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.2s ease, border-color 0.2s ease'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {skill.name}
                  </h3>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      padding: '0.25rem 0.6rem',
                      borderRadius: '6px',
                      background: 'rgba(0, 242, 254, 0.08)',
                      color: 'var(--accent-cyan)',
                      border: '1px solid rgba(0, 242, 254, 0.2)'
                    }}
                  >
                    {skill.tag}
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '0.3rem' }}>
                  <span>Proficiency</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>{skill.level}%</span>
                </div>
                <div
                  style={{
                    width: '100%',
                    height: '6px',
                    borderRadius: '9999px',
                    background: 'rgba(255, 255, 255, 0.08)',
                    overflow: 'hidden'
                  }}
                >
                  <div
                    style={{
                      width: `${skill.level}%`,
                      height: '100%',
                      background: 'var(--grad-cyber)',
                      borderRadius: '9999px',
                      transition: 'width 1s ease-in-out'
                    }}
                  />
                </div>
              </div>

            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
