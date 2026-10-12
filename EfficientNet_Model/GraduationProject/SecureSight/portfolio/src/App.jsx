import React, { useState, useEffect } from 'react';
import NeuralCanvas from './components/NeuralCanvas';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import About from './components/About';
import Skills from './components/Skills';
import Projects from './components/Projects';
import RagLab from './components/RagLab';
import ExperienceTimeline from './components/ExperienceTimeline';
import Certifications from './components/Certifications';
import ContactModal from './components/ContactModal';
import { ResumeModal, ProjectModal } from './components/Modals';
import { Cpu, Heart, Linkedin, Mail, ArrowUp } from 'lucide-react';

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [isResumeOpen, setIsResumeOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleOpenContact = () => {
    const contactSection = document.getElementById('contact');
    if (contactSection) {
      contactSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div style={{ minHeight: '100vh', position: 'relative' }}>
      
      {/* Background Interactive Neural Grid */}
      <NeuralCanvas />

      {/* Glass Navigation Bar */}
      <Navbar
        theme={theme}
        toggleTheme={toggleTheme}
        onOpenResume={() => setIsResumeOpen(true)}
      />

      {/* Main Sections */}
      <main style={{ position: 'relative', zIndex: 1 }}>
        <Hero onOpenContact={handleOpenContact} />
        <About />
        <Skills />
        <Projects onSelectProject={(p) => setSelectedProject(p)} />
        <RagLab />
        <ExperienceTimeline />
        <Certifications />
        <ContactModal />
      </main>

      {/* Footer */}
      <footer
        style={{
          position: 'relative',
          zIndex: 1,
          background: 'var(--bg-secondary)',
          borderTop: '1px solid var(--border-glass)',
          padding: '3rem 0 2rem 0',
          fontSize: '0.9rem',
          color: 'var(--text-muted)'
        }}
      >
        <div className="container">
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}
          >
            <div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.3rem' }}>
                Tasneem<span className="text-gradient">.AI</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                B.Sc. Artificial Intelligence • Alamein International University (AIU)
              </p>
            </div>

            {/* Quick Links */}
            <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.88rem' }}>
              <a href="#about" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>About</a>
              <a href="#skills" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Skills</a>
              <a href="#projects" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Projects</a>
              <a href="#rag-lab" style={{ color: 'var(--accent-cyan)', textDecoration: 'none', fontWeight: 700 }}>RAG Lab ⚡</a>
              <a href="#contact" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Contact</a>
            </div>

            {/* Direct Connect Buttons */}
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <a
                href="https://www.linkedin.com/in/tasneem-ibrahim-46a204331"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn Profile"
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  background: 'var(--bg-glass)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--accent-indigo)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textDecoration: 'none'
                }}
              >
                <Linkedin size={18} />
              </a>

              <a
                href="mailto:tasneemibrahim.ai@gmail.com"
                aria-label="Email Tasneem"
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  background: 'var(--bg-glass)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--accent-cyan)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textDecoration: 'none'
                }}
              >
                <Mail size={18} />
              </a>
            </div>
          </div>

          <div
            style={{
              paddingTop: '1.5rem',
              borderTop: '1px solid var(--border-glass)',
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '0.82rem',
              color: 'var(--text-dim)'
            }}
          >
            <div>
              © {new Date().getFullYear()} Tasneem Ibrahim. All rights reserved.
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              Engineered with <Heart size={14} color="var(--accent-pink)" fill="var(--accent-pink)" /> using React & AI.
            </div>
          </div>
        </div>
      </footer>

      {/* Scroll To Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          aria-label="Scroll to top"
          style={{
            position: 'fixed',
            bottom: '2rem',
            right: '2rem',
            zIndex: 90,
            width: '45px',
            height: '45px',
            borderRadius: '50%',
            background: 'var(--grad-cyber)',
            border: 'none',
            color: '#000',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: '0 0 20px rgba(0, 242, 254, 0.4)',
            transition: 'transform 0.2s ease'
          }}
        >
          <ArrowUp size={20} strokeWidth={2.5} />
        </button>
      )}

      {/* Overlay Modals */}
      <ResumeModal
        isOpen={isResumeOpen}
        onClose={() => setIsResumeOpen(false)}
      />

      <ProjectModal
        project={selectedProject}
        onClose={() => setSelectedProject(null)}
      />

    </div>
  );
}
