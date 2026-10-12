import React from 'react';
import { GraduationCap, BookOpen, Cpu, Sparkles, Layers, Terminal, CheckCircle2 } from 'lucide-react';

export default function About() {
  const highlights = [
    {
      icon: <GraduationCap size={24} color="var(--accent-cyan)" />,
      title: "Alamein International University (AIU)",
      subtitle: "B.Sc. in Artificial Intelligence | GPA 3.2 / 4.0",
      desc: "Expected Graduation: June 2026 (Final Academic Phase). Rigorous training in AI theory, deep learning algorithms, computer vision, and data science."
    },
    {
      icon: <Sparkles size={24} color="var(--accent-purple)" />,
      title: "AI Research Assistant – RAG Systems",
      subtitle: "Academic Research Workflow AI Application",
      desc: "Architecting a Retrieval-Augmented Generation (RAG) system to enhance research retrieval, document embedding search, and automated answer synthesis."
    },
    {
      icon: <Cpu size={24} color="var(--accent-emerald)" />,
      title: "ITI Field Training Graduate",
      subtitle: "Information Technology Institute (3-Month Program)",
      desc: "Completed an intensive software development program. Built desktop and web software projects with focus on software engineering fundamentals."
    }
  ];

  const pillars = [
    {
      title: "Machine Learning & Deep Learning",
      desc: "Hands-on experience developing model architectures in PyTorch, TensorFlow, Keras, scikit-learn, and OpenCV for vision & NLP tasks.",
      icon: <Cpu size={20} color="var(--accent-cyan)" />
    },
    {
      title: "Full-Stack Web Development",
      desc: "Building responsive frontends in React.js paired with Node.js/Express REST APIs, MongoDB, and MySQL databases.",
      icon: <Layers size={20} color="var(--accent-purple)" />
    },
    {
      title: "DevOps, Cloud & MLOps",
      desc: "Containerization with Docker, Kubernetes orchestration, AWS cloud workflows, Kafka event streaming, and Git CI/CD.",
      icon: <Terminal size={20} color="var(--accent-emerald)" />
    }
  ];

  return (
    <section id="about" style={{ padding: '6rem 0', position: 'relative' }}>
      <div className="container">
        
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <div className="badge-glow" style={{ marginBottom: '0.75rem' }}>
            <BookOpen size={14} />
            <span>Background & Expertise</span>
          </div>
          <h2 className="section-title">
            About <span className="text-gradient">Tasneem Ibrahim</span>
          </h2>
          <p className="section-subtitle">
            Passionate AI Engineer bridging cutting-edge machine learning research with robust, scalable software engineering.
          </p>
        </div>

        {/* Top Grid: Highlights Timeline Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))',
            gap: '1.75rem',
            marginBottom: '4rem'
          }}
        >
          {highlights.map((item, index) => (
            <div
              key={index}
              className="glass-panel"
              style={{
                padding: '2rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  top: '-20px',
                  right: '-20px',
                  width: '90px',
                  height: '90px',
                  borderRadius: '50%',
                  background: 'var(--bg-glass)',
                  filter: 'blur(10px)',
                  pointerEvents: 'none'
                }}
              />
              <div>
                <div
                  style={{
                    width: '50px',
                    height: '50px',
                    borderRadius: '12px',
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid var(--border-glass)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '1.25rem'
                  }}
                >
                  {item.icon}
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.35rem', color: 'var(--text-main)' }}>
                  {item.title}
                </h3>
                <div style={{ fontSize: '0.88rem', color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: '0.85rem' }}>
                  {item.subtitle}
                </div>
                <p style={{ fontSize: '0.94rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Panel: Engineering Pillars */}
        <div
          className="glass-panel"
          style={{
            padding: '2.5rem',
            background: 'linear-gradient(135deg, rgba(13, 17, 26, 0.8) 0%, rgba(18, 24, 38, 0.9) 100%)'
          }}
        >
          <h3 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '1.75rem', textAlign: 'center' }}>
            Core <span className="text-gradient">Engineering Pillars</span>
          </h3>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '1.75rem'
            }}
          >
            {pillars.map((pillar, i) => (
              <div
                key={i}
                style={{
                  padding: '1.25rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-glass)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.6rem' }}>
                  {pillar.icon}
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {pillar.title}
                  </h4>
                </div>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  {pillar.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
}
