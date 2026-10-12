import React from 'react';
import { Briefcase, GraduationCap, Award, Calendar, MapPin, CheckCircle2 } from 'lucide-react';

export default function ExperienceTimeline() {
  const experiences = [
    {
      type: 'work',
      title: 'AI Research Assistant – RAG System Development',
      organization: 'Academic AI Research Lab',
      period: '2025 – Present (Ongoing)',
      location: 'Alamein, Egypt',
      status: 'Deployed & Under Evaluation',
      description: 'Developing a full-stack Retrieval-Augmented Generation (RAG) web application tailored for academic research document search and automated literature synthesis.',
      points: [
        'Built dense vector embedding retrieval pipelines using custom prompt templates.',
        'Deployed system for user testing to accelerate scientific literature search workflows.',
        'Evaluated retrieval precision and LLM hallucination mitigation benchmarks.'
      ],
      icon: <Briefcase size={18} color="var(--accent-cyan)" />
    },
    {
      type: 'training',
      title: 'Information Technology Institute (ITI) Field Training',
      organization: 'Information Technology Institute (ITI)',
      period: '3-Month Intensive Program',
      location: 'Egypt',
      status: 'Certified Graduate',
      description: 'Completed a rigorous 3-month intensive software development program focused on full-stack web, desktop application engineering, and structured SDLC principles.',
      points: [
        'Built a complete desktop application project with clean object-oriented architecture.',
        'Gained hands-on experience in Java, SQL relational database design, and REST APIs.',
        'Received ITI Field Training Certification.'
      ],
      icon: <Award size={18} color="var(--accent-purple)" />
    },
    {
      type: 'education',
      title: 'Bachelor of Science in Artificial Intelligence',
      organization: 'Alamein International University (AIU)',
      period: 'Oct 2022 – Expected June 2026',
      location: 'Alamein, Egypt',
      status: 'GPA: 3.2 / 4.0 (Final Academic Phase)',
      description: 'Pursuing specialized AI degree focused on machine learning algorithms, deep neural networks, computer vision, natural language processing, and software systems.',
      points: [
        'Current Academic Status: Final Phase (Graduating May/June 2026).',
        'Graduation Project: SecureSight (EfficientNet Deep Learning Vision Model).',
        'Strong academic foundation in linear algebra, probability, data structures, and algorithms.'
      ],
      icon: <GraduationCap size={18} color="var(--accent-emerald)" />
    }
  ];

  return (
    <section id="experience" style={{ padding: '6rem 0', position: 'relative' }}>
      <div className="container">
        
        {/* Section Title */}
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <div className="badge-glow" style={{ marginBottom: '0.75rem' }}>
            <Calendar size={14} />
            <span>Career & Academic Journey</span>
          </div>
          <h2 className="section-title">
            Experience & <span className="text-gradient">Education</span>
          </h2>
          <p className="section-subtitle">
            A timeline of Tasneem's academic pursuits, AI research assistantship, and intensive software engineering training.
          </p>
        </div>

        {/* Timeline Container */}
        <div style={{ maxWidth: '800px', margin: '0 auto', position: 'relative' }}>
          
          {/* Vertical Glowing Line */}
          <div
            style={{
              position: 'absolute',
              left: '24px',
              top: '15px',
              bottom: '15px',
              width: '2px',
              background: 'linear-gradient(180deg, var(--accent-cyan) 0%, var(--accent-purple) 50%, var(--accent-emerald) 100%)',
              opacity: 0.4
            }}
          />

          {experiences.map((exp, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: '1.75rem',
                marginBottom: '2.5rem',
                position: 'relative'
              }}
            >
              {/* Timeline Node Badge */}
              <div
                style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '50%',
                  background: 'var(--bg-secondary)',
                  border: '2px solid var(--accent-cyan)',
                  boxShadow: '0 0 15px rgba(0, 242, 254, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  zIndex: 2
                }}
              >
                {exp.icon}
              </div>

              {/* Content Card */}
              <div className="glass-panel" style={{ flex: 1, padding: '1.75rem' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>
                    {exp.title}
                  </h3>
                  <span
                    style={{
                      fontSize: '0.78rem',
                      fontFamily: 'var(--font-mono)',
                      padding: '0.25rem 0.65rem',
                      borderRadius: '9999px',
                      background: 'rgba(0, 242, 254, 0.08)',
                      color: 'var(--accent-cyan)',
                      border: '1px solid rgba(0, 242, 254, 0.25)'
                    }}
                  >
                    {exp.period}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.85rem', flexWrap: 'wrap' }}>
                  <strong style={{ color: 'var(--accent-purple)' }}>{exp.organization}</strong>
                  <span>•</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}><MapPin size={13} /> {exp.location}</span>
                  <span>•</span>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>{exp.status}</span>
                </div>

                <p style={{ fontSize: '0.94rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '1rem' }}>
                  {exp.description}
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {exp.points.map((pt, pIdx) => (
                    <div key={pIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.88rem', color: 'var(--text-main)' }}>
                      <CheckCircle2 size={15} color="var(--accent-cyan)" style={{ marginTop: '0.2rem', flexShrink: 0 }} />
                      <span>{pt}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          ))}

        </div>

      </div>
    </section>
  );
}
