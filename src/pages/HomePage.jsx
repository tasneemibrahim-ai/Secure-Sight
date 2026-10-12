import { useEffect, useRef, useState } from 'react';
import {
  Shield, Camera, Brain, Bell, MapPin, Layers, Activity,
  ChevronRight, Play, ArrowRight, Menu, X, Zap, Eye,
  Clock, CheckCircle, AlertTriangle, Flame, HeartPulse,
  ShieldCheck, Lock, Radio, MonitorCheck, Cpu, Network
} from 'lucide-react';

// ─── Mock Data ───────────────────────────────────────────────────────────────

const NAV_LINKS = ['About Us', 'Technology', 'Pricing', 'Contact'];

const STATS = [
  { value: 99.7, suffix: '%', label: 'Detection Accuracy', icon: CheckCircle },
  { value: 2,   prefix: '<', suffix: 's', label: 'Response Time', icon: Zap },
  { value: 24,  suffix: '/7', label: 'Monitoring', icon: Clock },
  { value: 3,   suffix: '',  label: 'Subscriber Types', icon: Shield },
];

const FEATURES = [
  {
    id: 'f1',
    icon: MapPin,
    title: 'Real-Time Urban Analytics',
    description: 'City-wide heatmap visualization with live threat density mapping across all monitored zones.',
    color: '#00E5FF',
    delay: '0ms',
  },
  {
    id: 'f2',
    icon: Layers,
    title: 'Glassmorphism Interface',
    description: 'Sleek, modern UI built for clarity under pressure — every alert surface-rendered at a glance.',
    color: '#6366F1',
    delay: '100ms',
  },
  {
    id: 'f3',
    icon: Activity,
    title: 'Heatmap Visualization',
    description: 'Real-time threat intensity overlays update every 800ms — never miss a developing situation.',
    color: '#10B981',
    delay: '200ms',
  },
];

const HOW_IT_WORKS = [
  {
    step: '01',
    icon: Camera,
    title: 'Camera Detects Activity',
    description: 'CCTV cameras continuously capture footage across all monitored zones, streaming to the AI engine.',
  },
  {
    step: '02',
    icon: Brain,
    title: 'AI Analyses in Real-Time',
    description: 'Our Two-Stream AI model  classifies threats in under 800 milliseconds.',
  },
  {
    step: '03',
    icon: Bell,
    title: 'Instant Alert Dispatched',
    description: 'Alrets routed to targeted alerts directly to Users.',
  },
];

const SUBSCRIBERS = [
  {
    icon: '🚔',
    role: 'Police',
    color: '#3B82F6',
    glowColor: 'rgba(59, 130, 246, 0.25)',
    borderColor: 'rgba(59, 130, 246, 0.4)',
    alerts: ['Theft & Robbery', 'Physical Altercations', 'Vandalism', 'Suspicious Activity'],
    stat: '4 alert categories',
  },
  {
    icon: '🏥',
    role: 'Hospital',
    color: '#10B981',
    glowColor: 'rgba(16, 185, 129, 0.25)',
    borderColor: 'rgba(16, 185, 129, 0.4)',
    alerts: ['Injury Detection', 'Person Down', 'Medical Emergency', 'Crowd Crush'],
    stat: '4 alert categories',
  },
  {
    icon: '🚒',
    role: 'Firefighters',
    color: '#F59E0B',
    glowColor: 'rgba(245, 158, 11, 0.25)',
    borderColor: 'rgba(245, 158, 11, 0.4)',
    alerts: ['Fire Detected', 'Smoke Detection', 'Explosion Event', 'Gas Leak Risk'],
    stat: '4 alert categories',
  },
];

// ─── Utility hooks ────────────────────────────────────────────────────────────

function useScrolled(threshold = 50) {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > threshold);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [threshold]);
  return scrolled;
}

function useIntersectionObserver(options = {}) {
  const ref = useRef(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setInView(true); observer.disconnect(); } },
      { threshold: 0.15, ...options }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [options]);
  return [ref, inView];
}

function useCountUp(target, duration = 1800, inView = false) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!inView) return;
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= target) { setCount(target); clearInterval(timer); }
      else { setCount(Number(start.toFixed(target % 1 !== 0 ? 1 : 0))); }
    }, 16);
    return () => clearInterval(timer);
  }, [inView, target, duration]);
  return count;
}

// ─── Sub-Components ───────────────────────────────────────────────────────────

function StatItem({ stat, inView }) {
  const count = useCountUp(stat.value, 1600, inView);
  const Icon = stat.icon;
  return (
    <div className="flex flex-col items-center gap-2 px-6 py-4">
      <Icon size={20} className="text-[#00E5FF] opacity-70" />
      <div className="font-black text-3xl sm:text-4xl text-white tracking-tight font-mono">
        {stat.prefix && <span className="text-[#00E5FF]">{stat.prefix}</span>}
        {count}
        <span className="text-[#00E5FF]">{stat.suffix}</span>
      </div>
      <div className="text-sm text-slate-400 text-center font-medium">{stat.label}</div>
    </div>
  );
}

// ─── Animated Orb (Hero Right Panel) ─────────────────────────────────────────

function AIOrb() {
  return (
    <div className="relative flex items-center justify-center w-full h-full min-h-[420px] select-none">
      {/* Outer glow rings */}
      <div
        className="absolute rounded-full border border-[#00E5FF]/10 animate-ping-slow"
        style={{ width: 380, height: 380 }}
      />
      <div
        className="absolute rounded-full border border-[#00E5FF]/15"
        style={{ width: 320, height: 320 }}
      />
      <div
        className="absolute rounded-full border border-[#00E5FF]/20"
        style={{ width: 270, height: 270 }}
      />

      {/* Rotating orbit rings */}
      <div
        className="absolute rounded-full border border-dashed border-[#00E5FF]/20 animate-spin-slow"
        style={{ width: 310, height: 310 }}
      />

      {/* Camera icons orbiting */}
      {[0, 90, 180, 270].map((deg, i) => (
        <div
          key={i}
          className="absolute"
          style={{
            width: 320,
            height: 320,
            transform: `rotate(${deg}deg)`,
            animation: `spin 20s linear infinite`,
          }}
        >
          <div
            className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2"
            style={{ transform: `translateX(-50%) translateY(-50%) rotate(-${deg}deg)` }}
          >
            <div
              className="w-10 h-10 rounded-full glass flex items-center justify-center border border-[#00E5FF]/30"
              style={{ boxShadow: '0 0 15px rgba(0, 229, 255, 0.3)' }}
            >
              <Camera size={16} className="text-[#00E5FF]" />
            </div>
          </div>
        </div>
      ))}

      {/* Core glowing orb */}
      <div
        className="relative rounded-full flex items-center justify-center animate-glow-pulse"
        style={{
          width: 160,
          height: 160,
          background: 'radial-gradient(circle at center, rgba(0,229,255,0.25) 0%, rgba(0,100,200,0.15) 50%, transparent 70%)',
          border: '2px solid rgba(0, 229, 255, 0.5)',
          boxShadow: '0 0 60px rgba(0, 229, 255, 0.4), inset 0 0 40px rgba(0, 229, 255, 0.1)',
        }}
      >
        {/* Scan line sweep */}
        <div
          className="absolute inset-0 rounded-full overflow-hidden"
          style={{ clipPath: 'circle(50%)' }}
        >
          <div
            className="absolute left-0 right-0 h-px animate-scan"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(0,229,255,0.8), transparent)',
              top: '0%',
            }}
          />
        </div>

        {/* Eye iris */}
        <div
          className="rounded-full flex items-center justify-center"
          style={{
            width: 80,
            height: 80,
            background: 'radial-gradient(circle, #001a2e 0%, #000d1a 100%)',
            border: '2px solid rgba(0, 229, 255, 0.4)',
          }}
        >
          <div
            className="rounded-full animate-pulse-slow"
            style={{
              width: 36,
              height: 36,
              background: 'radial-gradient(circle, #00E5FF 0%, #0099CC 60%, #003366 100%)',
              boxShadow: '0 0 20px rgba(0, 229, 255, 0.8)',
            }}
          />
        </div>
      </div>

      {/* Data fragments */}
      {[
        { text: 'THREAT: NONE', x: '75%', y: '15%', delay: '0s' },
        { text: 'CAM-07 ACTIVE', x: '10%', y: '20%', delay: '1s' },
        { text: 'AI: SCANNING', x: '65%', y: '78%', delay: '2s' },
        { text: '0x4A2F', x: '5%', y: '72%', delay: '0.5s' },
        { text: 'CONF: 99.7%', x: '60%', y: '45%', delay: '1.5s' },
      ].map((frag, i) => (
        <div
          key={i}
          className="absolute text-[10px] font-mono text-[#00E5FF]/40 pointer-events-none"
          style={{
            left: frag.x,
            top: frag.y,
            animation: `pulse 3s ease-in-out infinite`,
            animationDelay: frag.delay,
          }}
        >
          {frag.text}
        </div>
      ))}

      {/* Status badges */}
      <div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-1.5 px-3 py-1.5 rounded-full"
        style={{ background: 'rgba(0, 229, 255, 0.1)', border: '1px solid rgba(0,229,255,0.3)' }}
      >
        <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-[10px] font-mono text-[#00E5FF] font-medium tracking-widest">SYSTEM ONLINE</span>
      </div>
    </div>
  );
}

// ─── Feature Card ─────────────────────────────────────────────────────────────

function FeatureCard({ feature, inView }) {
  const Icon = feature.icon;
  return (
    <div
      className="glass glass-hover rounded-2xl p-8 flex flex-col gap-5 cursor-default"
      style={{
        opacity: inView ? 1 : 0,
        transform: inView ? 'translateY(0)' : 'translateY(30px)',
        transition: `opacity 0.6s ease ${feature.delay}, transform 0.6s ease ${feature.delay}`,
      }}
    >
      <div
        className="w-14 h-14 rounded-xl flex items-center justify-center"
        style={{
          background: `${feature.color}15`,
          border: `1px solid ${feature.color}30`,
          boxShadow: `0 0 20px ${feature.color}20`,
        }}
      >
        <Icon size={24} style={{ color: feature.color }} />
      </div>
      <div>
        <h3 className="text-lg font-bold text-white mb-2 leading-snug">{feature.title}</h3>
        <p className="text-slate-400 text-sm leading-relaxed">{feature.description}</p>
      </div>
      <div
        className="mt-auto flex items-center gap-1 text-sm font-semibold"
        style={{ color: feature.color }}
      >
        Learn more <ArrowRight size={14} />
      </div>
    </div>
  );
}

// ─── Step Card ────────────────────────────────────────────────────────────────

function StepCard({ step, index, total, inView }) {
  const Icon = step.icon;
  return (
    <div className="relative flex flex-col items-center text-center gap-4 group">
      {/* Connecting line */}
      {index < total - 1 && (
        <div className="hidden lg:block absolute top-12 left-[calc(50%+52px)] right-[calc(-50%+52px)] z-0">
          <div
            className="h-px"
            style={{
              background: 'linear-gradient(90deg, rgba(0,229,255,0.5), rgba(0,229,255,0.1))',
            }}
          />
          <div
            className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t-2 border-r-2 border-[#00E5FF]/50"
            style={{ transform: 'translateY(-50%) rotate(45deg)' }}
          />
        </div>
      )}

      {/* Step circle */}
      <div
        className="relative z-10 w-24 h-24 rounded-full flex items-center justify-center glass"
        style={{
          border: '2px solid rgba(0, 229, 255, 0.3)',
          boxShadow: '0 0 30px rgba(0, 229, 255, 0.15)',
          opacity: inView ? 1 : 0,
          transform: inView ? 'scale(1)' : 'scale(0.8)',
          transition: `opacity 0.5s ease ${index * 150}ms, transform 0.5s ease ${index * 150}ms`,
        }}
      >
        <Icon size={32} className="text-[#00E5FF]" />
        <span
          className="absolute -top-2 -right-2 w-7 h-7 rounded-full flex items-center justify-center text-xs font-black font-mono text-navy"
          style={{ background: '#00E5FF', boxShadow: '0 0 10px rgba(0,229,255,0.6)' }}
        >
          {step.step}
        </span>
      </div>

      <div
        style={{
          opacity: inView ? 1 : 0,
          transform: inView ? 'translateY(0)' : 'translateY(16px)',
          transition: `opacity 0.5s ease ${index * 150 + 100}ms, transform 0.5s ease ${index * 150 + 100}ms`,
        }}
      >
        <h3 className="text-base font-bold text-white mb-1.5">{step.title}</h3>
        <p className="text-slate-400 text-sm leading-relaxed max-w-[220px] mx-auto">{step.description}</p>
      </div>
    </div>
  );
}

// ─── Subscriber Card ──────────────────────────────────────────────────────────

function SubscriberCard({ sub, index, inView }) {
  return (
    <div
      className="rounded-2xl p-8 flex flex-col gap-5 cursor-default transition-all duration-300 group"
      style={{
        background: 'rgba(255,255,255,0.03)',
        border: `1px solid ${sub.borderColor}`,
        backdropFilter: 'blur(20px)',
        opacity: inView ? 1 : 0,
        transform: inView ? 'translateY(0)' : 'translateY(30px)',
        transition: `opacity 0.6s ease ${index * 120}ms, transform 0.6s ease ${index * 120}ms, box-shadow 0.3s ease, background 0.3s ease`,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.boxShadow = `0 20px 60px rgba(0,0,0,0.5), 0 0 40px ${sub.glowColor}`;
        e.currentTarget.style.background = `rgba(255,255,255,0.06)`;
        e.currentTarget.style.transform = 'translateY(-6px)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.boxShadow = 'none';
        e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-4">
        <div
          className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl"
          style={{ background: sub.glowColor, border: `1px solid ${sub.borderColor}` }}
        >
          {sub.icon}
        </div>
        <div>
          <h3 className="text-xl font-bold text-white">{sub.role}</h3>
          <span
            className="text-xs font-mono font-medium px-2 py-0.5 rounded-full"
            style={{ color: sub.color, background: sub.glowColor }}
          >
            {sub.stat}
          </span>
        </div>
      </div>

      {/* Alert list */}
      <ul className="flex flex-col gap-2.5">
        {sub.alerts.map((alert, i) => (
          <li key={i} className="flex items-center gap-3 text-sm text-slate-300">
            <div
              className="w-1.5 h-1.5 rounded-full flex-shrink-0"
              style={{ background: sub.color, boxShadow: `0 0 6px ${sub.color}` }}
            />
            {alert}
          </li>
        ))}
      </ul>

      {/* CTA */}
      <button
        className="mt-auto text-sm font-semibold flex items-center gap-1.5 transition-all duration-200 group-hover:gap-2.5"
        style={{ color: sub.color }}
      >
        View Dashboard <ArrowRight size={14} />
      </button>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function HomePage() {
  const scrolled = useScrolled(50);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const [statsRef, statsInView]           = useIntersectionObserver();
  const [featuresRef, featuresInView]     = useIntersectionObserver();
  const [howRef, howInView]               = useIntersectionObserver();
  const [subsRef, subsInView]             = useIntersectionObserver();
  const [heroRef, heroInView]             = useIntersectionObserver({ threshold: 0.05 });

  return (
    <div className="min-h-screen bg-navy overflow-x-hidden">

      {/* ── NAVBAR ── */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
        style={{
          background: scrolled ? 'rgba(10, 15, 30, 0.92)' : 'transparent',
          backdropFilter: scrolled ? 'blur(20px)' : 'none',
          borderBottom: scrolled ? '1px solid rgba(255,255,255,0.06)' : 'none',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">

            {/* Logo */}
            <a href="#" className="flex items-center gap-2.5 group">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 group-hover:scale-110"
                style={{
                  background: 'rgba(0,229,255,0.12)',
                  border: '1px solid rgba(0,229,255,0.4)',
                  boxShadow: '0 0 15px rgba(0,229,255,0.2)',
                }}
              >
                <Shield size={18} className="text-[#00E5FF]" />
              </div>
              <span className="text-lg font-bold tracking-tight">
                <span className="text-white">Secure</span>
                <span className="text-[#00E5FF]">Sight</span>
              </span>
            </a>

            {/* Desktop nav */}
            <div className="hidden lg:flex items-center gap-8">
              {NAV_LINKS.map(link => (
                <a
                  key={link}
                  href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
                  className="text-sm font-medium text-slate-300 hover:text-[#00E5FF] transition-colors duration-200 relative group"
                >
                  {link}
                  <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-[#00E5FF] group-hover:w-full transition-all duration-200" />
                </a>
              ))}
            </div>

            {/* Auth buttons */}
            <div className="hidden lg:flex items-center gap-3">
              <a
                href="/login"
                className="btn-outline text-sm"
                id="nav-login"
              >
                Login
              </a>
              <a
                href="/signup"
                className="btn-cyan text-sm"
                id="nav-get-started"
              >
                Get Started →
              </a>
            </div>

            {/* Mobile hamburger */}
            <button
              id="mobile-menu-toggle"
              className="lg:hidden w-10 h-10 flex items-center justify-center rounded-lg glass text-slate-300"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle mobile menu"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile menu drawer */}
        <div
          className="lg:hidden overflow-hidden transition-all duration-300"
          style={{ maxHeight: mobileMenuOpen ? '400px' : '0' }}
        >
          <div className="px-4 py-4 border-t border-white/5 flex flex-col gap-1"
            style={{ background: 'rgba(10,15,30,0.98)', backdropFilter: 'blur(20px)' }}
          >
            {NAV_LINKS.map(link => (
              <a
                key={link}
                href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
                className="px-4 py-3 rounded-lg text-slate-300 hover:text-[#00E5FF] hover:bg-white/5 transition-all duration-200 text-sm font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                {link}
              </a>
            ))}
            <div className="flex flex-col gap-2 mt-3 pt-3 border-t border-white/5">
              <a href="/login" className="btn-outline text-sm text-center">Login</a>
              <a href="/signup" className="btn-cyan text-sm text-center">Get Started →</a>
            </div>
          </div>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section
        ref={heroRef}
        id="hero"
        className="relative min-h-screen flex items-center overflow-hidden"
        style={{
          background: 'radial-gradient(ellipse 80% 60% at 70% 50%, rgba(0,80,150,0.2) 0%, transparent 60%), radial-gradient(ellipse 40% 80% at 10% 50%, rgba(0,50,100,0.15) 0%, transparent 60%), #0A0F1E',
        }}
      >
        {/* Background grid */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: 'linear-gradient(rgba(0,229,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,255,1) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />

        {/* Floating particles */}
        {[
          { style: { left: '15%', top: '30%', width: 4, height: 4 } },
          { style: { left: '80%', top: '20%', width: 3, height: 3 } },
          { style: { left: '50%', top: '70%', width: 5, height: 5 } },
          { style: { left: '25%', top: '75%', width: 3, height: 3 } },
          { style: { left: '70%', top: '65%', width: 4, height: 4 } },
        ].map((p, i) => (
          <div
            key={i}
            className="absolute rounded-full animate-pulse-slow"
            style={{
              ...p.style,
              background: '#00E5FF',
              boxShadow: '0 0 10px rgba(0,229,255,0.8)',
              animationDelay: `${i * 0.7}s`,
            }}
          />
        ))}

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <div className="grid lg:grid-cols-[60%_40%] items-center gap-12 lg:gap-0 pt-20 lg:pt-0 pb-12 lg:pb-0 min-h-screen">

            {/* Left — copy */}
            <div
              className="flex flex-col gap-8"
              style={{
                opacity: heroInView ? 1 : 0,
                transform: heroInView ? 'translateX(0)' : 'translateX(-40px)',
                transition: 'opacity 0.8s ease, transform 0.8s ease',
              }}
            >
              {/* Label */}
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] animate-pulse" />
                <span className="text-xs font-mono font-semibold tracking-[0.25em] text-[#00E5FF] uppercase">
                  AI-Powered Surveillance
                </span>
              </div>

              {/* Headline */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-[1.05] tracking-tight text-white">
                Surveillance That{' '}
                <span
                  className="text-gradient"
                  style={{
                    background: 'linear-gradient(135deg, #00E5FF 0%, #0099FF 60%, #6366F1 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Understands,
                </span>{' '}
                Acts, and Protects
              </h1>

              {/* Subtitle */}
              <p className="text-lg text-slate-400 leading-relaxed max-w-xl font-light">
                Revolutionizing security through advanced AI and proactive urban intelligence —
                detecting threats, routing alerts, and protecting communities in real time.
              </p>

              {/* Badges */}
              <div className="flex flex-wrap gap-3">
                {['ResNet-50', 'R(2+1)D', 'ViT Transformer', 'MQTT Routing'].map(badge => (
                  <span
                    key={badge}
                    className="px-3 py-1 rounded-full text-xs font-mono font-medium"
                    style={{
                      background: 'rgba(0,229,255,0.08)',
                      border: '1px solid rgba(0,229,255,0.2)',
                      color: 'rgba(0,229,255,0.8)',
                    }}
                  >
                    {badge}
                  </span>
                ))}
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-wrap gap-4">
                <a
                  href="/login"
                  id="hero-live-demo"
                  className="btn-cyan inline-flex items-center gap-2 text-base"
                >
                  <Play size={16} className="fill-current" />
                  Live Demo
                  <ChevronRight size={16} className="-ml-1" />
                </a>
                <a
                  href="#contact"
                  id="hero-quote"
                  className="btn-outline inline-flex items-center gap-2 text-base"
                >
                  Request a Quote
                </a>
              </div>

              {/* Trust indicators */}
              
            </div>

            {/* Right — animated orb */}
            <div
              style={{
                opacity: heroInView ? 1 : 0,
                transform: heroInView ? 'translateX(0)' : 'translateX(40px)',
                transition: 'opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s',
              }}
            >
              <AIOrb />
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-bounce">
          <span className="text-xs text-slate-600 font-mono tracking-widest">SCROLL</span>
          <div className="w-px h-8 bg-gradient-to-b from-[#00E5FF]/40 to-transparent" />
        </div>
      </section>

      {/* ── STATS BAR ── */}
      <section ref={statsRef} id="stats" className="relative py-6 border-y border-white/5">
        <div
          className="absolute inset-0"
          style={{ background: 'rgba(0, 229, 255, 0.03)' }}
        />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 divide-x divide-white/5">
            {STATS.map((stat, i) => (
              <StatItem key={i} stat={stat} inView={statsInView} />
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section
        ref={featuresRef}
        id="technology"
        className="section-padding"
      >
        <div className="max-content">
          {/* Section header */}
          <div
            className="text-center mb-16"
            style={{
              opacity: featuresInView ? 1 : 0,
              transform: featuresInView ? 'translateY(0)' : 'translateY(20px)',
              transition: 'opacity 0.6s ease, transform 0.6s ease',
            }}
          >
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#00E5FF]/60" />
              <span className="text-xs font-mono font-semibold tracking-[0.2em] text-[#00E5FF] uppercase">
                Platform Features
              </span>
              <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#00E5FF]/60" />
            </div>
            <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              How SecureSight <span style={{ color: '#00E5FF' }}>Protects</span> You
            </h2>
            <p className="mt-4 text-slate-400 max-w-xl mx-auto leading-relaxed">
              A unified intelligence layer that sees, thinks, and acts — keeping your city
              safe around the clock.
            </p>
          </div>

          {/* Cards grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map(feature => (
              <FeatureCard key={feature.id} feature={feature} inView={featuresInView} />
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section
        ref={howRef}
        id="about-us"
        className="section-padding"
        style={{ background: 'rgba(255,255,255,0.01)' }}
      >
        <div className="max-content">
          {/* Header */}
          <div
            className="text-center mb-20"
            style={{
              opacity: howInView ? 1 : 0,
              transform: howInView ? 'translateY(0)' : 'translateY(20px)',
              transition: 'opacity 0.6s ease, transform 0.6s ease',
            }}
          >
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#00E5FF]/60" />
              <span className="text-xs font-mono font-semibold tracking-[0.2em] text-[#00E5FF] uppercase">
                The Pipeline
              </span>
              <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#00E5FF]/60" />
            </div>
            <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              How It Works
            </h2>
            <p className="mt-4 text-slate-400 max-w-lg mx-auto leading-relaxed">
              From camera capture to responder dispatch — the entire pipeline runs in under two seconds.
            </p>
          </div>

          {/* Steps */}
          <div className="grid lg:grid-cols-3 gap-12 lg:gap-6 relative">
            {HOW_IT_WORKS.map((step, i) => (
              <StepCard
                key={step.step}
                step={step}
                index={i}
                total={HOW_IT_WORKS.length}
                inView={howInView}
              />
            ))}
          </div>

          {/* Bottom CTA */}
          <div
            className="mt-20 text-center"
            style={{
              opacity: howInView ? 1 : 0,
              transition: 'opacity 0.6s ease 0.5s',
            }}
          >
            <div
              className="inline-flex items-center gap-3 px-6 py-4 rounded-2xl glass"
              style={{ border: '1px solid rgba(0,229,255,0.2)' }}
            >
              <Zap size={18} className="text-[#00E5FF]" />
              
              <span className="font-black font-mono text-[#00E5FF] text-lg">&lt;800ms</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── ALERT TYPES / SUBSCRIBERS ── */}
      <section ref={subsRef} id="pricing" className="section-padding">
        <div className="max-content">
          {/* Header */}
          <div
            className="text-center mb-16"
            style={{
              opacity: subsInView ? 1 : 0,
              transform: subsInView ? 'translateY(0)' : 'translateY(20px)',
              transition: 'opacity 0.6s ease, transform 0.6s ease',
            }}
          >
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#00E5FF]/60" />
              <span className="text-xs font-mono font-semibold tracking-[0.2em] text-[#00E5FF] uppercase">
                Subscriber Roles
              </span>
              <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#00E5FF]/60" />
            </div>
            <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              The Right Alert,{' '}
              <span style={{ color: '#00E5FF' }}>Every Time</span>
            </h2>
            <p className="mt-4 text-slate-400 max-w-xl mx-auto leading-relaxed">
              SecureSight routes each threat event to exactly the right responder —
              no noise, no missed alerts.
            </p>
          </div>

          {/* Cards */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {SUBSCRIBERS.map((sub, i) => (
              <SubscriberCard key={sub.role} sub={sub} index={i} inView={subsInView} />
            ))}
          </div>

          {/* Admin note */}
          <div
            className="mt-10 text-center"
            style={{
              opacity: subsInView ? 1 : 0,
              transition: 'opacity 0.6s ease 0.4s',
            }}
          >
            <p className="text-sm text-slate-500">
              <span className="text-slate-400 font-medium">🔐 Admin role</span> — manages all
              subscribers, assigns responder types, and has cross-category visibility.
            </p>
          </div>
        </div>
      </section>

      {/* ── CTA BAND ── */}
      <section
        id="contact"
        className="relative py-24 overflow-hidden"
        style={{
          background: 'radial-gradient(ellipse 60% 80% at 50% 50%, rgba(0,80,150,0.25) 0%, transparent 70%), #0A0F1E',
        }}
      >
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: 'linear-gradient(rgba(0,229,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,255,1) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
        />
        <div className="relative max-content text-center px-4">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight mb-6 leading-tight">
            Ready to Secure Your City?
          </h2>
          <p className="text-slate-400 text-lg max-w-xl mx-auto mb-10 leading-relaxed">
            Join police departments, hospitals, and fire stations already using
            SecureSight to protect their communities.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <a
              href="/signup"
              id="cta-get-started"
              className="btn-cyan text-base inline-flex items-center gap-2"
            >
              Get Started Free <ArrowRight size={16} />
            </a>
            <a
              href="/login"
              id="cta-sign-in"
              className="btn-outline text-base inline-flex items-center gap-2"
            >
              Sign In
            </a>
          </div>
          <p className="mt-6 text-xs text-slate-600">
            No credit card required. 30-day free trial. Cancel anytime.
          </p>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer
        id="footer"
        className="relative pt-16 pb-8 border-t border-white/5"
        style={{ background: 'rgba(6, 9, 20, 0.8)' }}
      >
        <div className="max-content px-4 sm:px-6 lg:px-8">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">

            {/* Brand */}
            <div className="lg:col-span-2 flex flex-col gap-4">
              <a href="#" className="flex items-center gap-2.5">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{
                    background: 'rgba(0,229,255,0.1)',
                    border: '1px solid rgba(0,229,255,0.3)',
                  }}
                >
                  <Shield size={16} className="text-[#00E5FF]" />
                </div>
                <span className="font-bold text-lg">
                  <span className="text-white">Secure</span>
                  <span className="text-[#00E5FF]">Sight</span>
                </span>
              </a>
              <p className="text-slate-500 text-sm leading-relaxed max-w-xs">
                AI-powered real-time surveillance that detects threats and instantly routes
                alerts to the right emergency responder.
              </p>
              <div className="flex items-center gap-2 text-xs font-mono text-slate-600">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                All systems operational
              </div>
            </div>

            {/* Product links */}
            <div>
              <h4 className="text-white font-semibold text-sm mb-4">Product</h4>
              <ul className="flex flex-col gap-2.5">
                {['About', 'Technology', 'Pricing', 'Changelog'].map(link => (
                  <li key={link}>
                    <a
                      href={`#${link.toLowerCase()}`}
                      className="text-slate-500 hover:text-[#00E5FF] text-sm transition-colors duration-200"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-white font-semibold text-sm mb-4">Legal & Support</h4>
              <ul className="flex flex-col gap-2.5">
                {['Privacy Policy', 'Terms of Service', 'Contact', 'Security'].map(link => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-slate-500 hover:text-[#00E5FF] text-sm transition-colors duration-200"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bottom bar */}
          <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-slate-600 text-xs">
              © 2025 SecureSight. All rights reserved.
            </p>
            <div className="flex items-center gap-1 text-slate-600 text-xs">
              Built with
              <span className="text-[#00E5FF] mx-1">♥</span>
              for public safety
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
