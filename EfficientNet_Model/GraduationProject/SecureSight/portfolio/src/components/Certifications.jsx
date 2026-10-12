import React from 'react';
import { Award, ShieldCheck, CheckCircle2, ExternalLink } from 'lucide-react';

export default function Certifications() {
  const certs = [
    {
      title: 'Information Technology Institute (ITI) Field Training Certificate',
      issuer: 'Information Technology Institute (ITI)',
      date: '2025',
      desc: 'Certified 3-month intensive software development & engineering program. Covered desktop development, OOP, and relational database systems.',
      color: 'var(--accent-cyan)'
    },
    {
      title: 'CCNA – Cisco Certified Network Associate',
      issuer: 'Cisco Systems',
      date: '2024',
      desc: 'Validated core knowledge in network fundamentals, IP connectivity, IP services, security fundamentals, and automation.',
      color: 'var(--accent-blue)'
    },
    {
      title: 'Coursera AI & Machine Learning Specialization Certificates',
      issuer: 'Coursera / DeepLearning.AI',
      date: '2024 - 2025',
      desc: 'Completed verified coursework in Neural Networks, Deep Learning, Supervised Learning, and Computer Vision.',
      color: 'var(--accent-purple)'
    },
    {
      title: 'Maharatech AI & Software Certifications',
      issuer: 'Maharatech Tech Platform',
      date: '2024',
      desc: 'Verified skills in Python programming, modern web technologies, and artificial intelligence fundamentals.',
      color: 'var(--accent-emerald)'
    }
  ];

  return (
    <section id="certifications" style={{ padding: '6rem 0', position: 'relative', background: 'var(--bg-secondary)' }}>
      <div className="container">
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <div className="badge-glow" style={{ marginBottom: '0.75rem' }}>
            <Award size={14} />
            <span>Verified Credentials</span>
          </div>
          <h2 className="section-title">
            Certifications & <span className="text-gradient">Training</span>
          </h2>
          <p className="section-subtitle">
            Official certifications validating expertise in ITI software engineering, Cisco networking, and machine learning platforms.
          </p>
        </div>

        {/* Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.75rem'
          }}
        >
          {certs.map((cert, idx) => (
            <div
              key={idx}
              className="glass-panel"
              style={{
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div
                    style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: '10px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid var(--border-glass)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <ShieldCheck size={22} color={cert.color} />
                  </div>
                  <span style={{ fontSize: '0.78rem', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                    {cert.date}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem', lineHeight: 1.35 }}>
                  {cert.title}
                </h3>

                <div style={{ fontSize: '0.85rem', color: cert.color, fontWeight: 600, marginBottom: '0.75rem' }}>
                  {cert.issuer}
                </div>

                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  {cert.desc}
                </p>
              </div>

              <div style={{ marginTop: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>
                <CheckCircle2 size={14} />
                <span>Verified Certificate</span>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
