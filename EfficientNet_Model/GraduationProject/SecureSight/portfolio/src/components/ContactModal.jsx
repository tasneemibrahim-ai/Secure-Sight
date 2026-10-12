import React, { useState } from 'react';
import { Mail, Phone, Linkedin, Github, Send, CheckCircle2, X, Copy, MapPin } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function ContactModal({ isOpen, onClose }) {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [sent, setSent] = useState(false);
  const [copied, setCopied] = useState(false);

  const workEmail = "tasneemibrahim.ai@gmail.com";
  const linkedinUrl = "https://www.linkedin.com/in/tasneem-ibrahim-46a204331";

  const handleSubmit = (e) => {
    e.preventDefault();
    setSent(true);
    confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
    setTimeout(() => {
      setSent(false);
      setFormData({ name: '', email: '', subject: '', message: '' });
      if (onClose) onClose();
    }, 2800);
  };

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(workEmail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="contact" style={{ padding: '6rem 0', position: 'relative' }}>
      <div className="container">
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <div className="badge-glow" style={{ marginBottom: '0.75rem' }}>
            <Mail size={14} />
            <span>Get In Touch</span>
          </div>
          <h2 className="section-title">
            Let's Build Something <span className="text-gradient">Intelligent</span>
          </h2>
          <p className="section-subtitle">
            Open for AI Engineering roles, research collaborations, software development projects, and internships.
          </p>
        </div>

        <div style={{ maxWidth: '960px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          
          {/* Left Column: Direct Info Cards */}
          <div className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '1.25rem' }}>
                Contact Information
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
                
                {/* Email Box */}
                <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-glass)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Work Email</span>
                    <button
                      onClick={handleCopyEmail}
                      style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.2rem', fontSize: '0.78rem' }}
                    >
                      <Copy size={13} /> {copied ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <a href={`mailto:${workEmail}`} style={{ color: 'var(--accent-cyan)', fontWeight: 700, textDecoration: 'none', fontSize: '0.98rem' }}>
                    {workEmail}
                  </a>
                </div>

                {/* LinkedIn Card */}
                <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-glass)' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem' }}>LinkedIn Profile</div>
                  <a href={linkedinUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-indigo)', fontWeight: 700, textDecoration: 'none', fontSize: '0.94rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Linkedin size={16} /> linkedin.com/in/tasneem-ibrahim
                  </a>
                </div>

                {/* Location & Status */}
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><MapPin size={15} color="var(--accent-pink)" /> Egypt</span>
                  <span>•</span>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>Open to Remote & Onsite</span>
                </div>

              </div>
            </div>

            <div style={{ padding: '1rem', borderRadius: 'var(--radius-sm)', background: 'rgba(0, 242, 254, 0.05)', border: '1px solid rgba(0, 242, 254, 0.2)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              ⚡ <strong>Response Time:</strong> Usually within 24 hours.
            </div>

          </div>

          {/* Right Column: Contact Form */}
          <div className="glass-panel" style={{ padding: '2rem', position: 'relative' }}>
            {sent ? (
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '2rem' }}>
                <CheckCircle2 size={56} color="var(--accent-emerald)" style={{ marginBottom: '1rem' }} />
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  Message Sent Successfully!
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
                  Thank you for reaching out to Tasneem. Your message has been routed to <strong>{workEmail}</strong>.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                    Your Name
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Dr. Sarah Vance / Recruiter"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(9, 13, 22, 0.8)',
                      border: '1px solid var(--border-glass)',
                      color: 'var(--text-main)',
                      outline: 'none',
                      fontSize: '0.9rem'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                    Your Email
                  </label>
                  <input
                    type="email"
                    required
                    placeholder="name@company.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(9, 13, 22, 0.8)',
                      border: '1px solid var(--border-glass)',
                      color: 'var(--text-main)',
                      outline: 'none',
                      fontSize: '0.9rem'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                    Subject
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="AI Engineering Role / Project Inquiry"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(9, 13, 22, 0.8)',
                      border: '1px solid var(--border-glass)',
                      color: 'var(--text-main)',
                      outline: 'none',
                      fontSize: '0.9rem'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                    Message
                  </label>
                  <textarea
                    required
                    rows={4}
                    placeholder="Write your message..."
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(9, 13, 22, 0.8)',
                      border: '1px solid var(--border-glass)',
                      color: 'var(--text-main)',
                      outline: 'none',
                      fontSize: '0.9rem',
                      resize: 'none'
                    }}
                  />
                </div>

                <button type="submit" className="btn-primary" style={{ width: '100%', padding: '0.85rem' }}>
                  <Send size={16} />
                  <span>Send Message to Tasneem</span>
                </button>
              </form>
            )}
          </div>

        </div>

      </div>
    </section>
  );
}
