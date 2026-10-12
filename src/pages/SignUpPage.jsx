import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle, Eye, EyeOff, Loader2, Lock, Mail, Shield, User } from 'lucide-react';

const PARTICLE_COUNT = 55;

function useParticles(canvasRef) {
  const stateRef = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let raf;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);

    stateRef.current = Array.from({ length: PARTICLE_COUNT }, (_, i) => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      r: Math.random() * 1.8 + 0.4,
      vx: (Math.random() - 0.5) * 0.22,
      vy: (Math.random() - 0.5) * 0.22,
      color: i % 9 === 0
        ? `rgba(255,80,80,${(Math.random() * 0.35 + 0.2).toFixed(2)})`
        : i % 4 === 0
          ? `rgba(255,255,255,${(Math.random() * 0.15 + 0.06).toFixed(2)})`
          : `rgba(0,229,255,${(Math.random() * 0.45 + 0.15).toFixed(2)})`,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: Math.random() * 0.02 + 0.005,
    }));

    const draw = () => {
      const W = canvas.width;
      const H = canvas.height;
      ctx.clearRect(0, 0, W, H);

      const pts = stateRef.current;

      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const dx = pts[i].x - pts[j].x;
          const dy = pts[i].y - pts[j].y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < 130) {
            ctx.beginPath();
            ctx.moveTo(pts[i].x, pts[i].y);
            ctx.lineTo(pts[j].x, pts[j].y);
            ctx.strokeStyle = `rgba(0,229,255,${((1 - d / 130) * 0.06).toFixed(3)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      pts.forEach((p) => {
        p.pulse += p.pulseSpeed;
        const alpha = 0.5 + 0.5 * Math.sin(p.pulse);
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = W;
        if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H;
        if (p.y > H) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * (0.8 + 0.2 * alpha), 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.shadowColor = p.color.includes('255,80') ? '#FF5050' : '#00E5FF';
        ctx.shadowBlur = 6 * alpha;
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
    };
  }, [canvasRef]);
}

function ParticleBackground() {
  const canvasRef = useRef(null);
  useParticles(canvasRef);
  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" aria-hidden="true" style={{ display: 'block' }} />;
}

function Field({ id, label, error, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[11px] font-bold tracking-[0.15em] text-slate-400 uppercase">
        {label}
      </label>
      {children}
      {error && (
        <div className="flex items-center gap-1.5 text-xs text-red-400" role="alert" style={{ animation: 'fadeSlideIn 0.2s ease' }}>
          <AlertCircle size={11} />
          {error}
        </div>
      )}
    </div>
  );
}

function TextInput({ id, type = 'text', value, onChange, placeholder, icon: Icon, rightSlot, autoComplete, disabled }) {
  const [focused, setFocused] = useState(false);

  return (
    <div
      className="flex items-center gap-3 px-3.5 rounded-xl transition-all duration-200"
      style={{
        background: 'rgba(255,255,255,0.05)',
        border: `1px solid ${focused ? 'rgba(0,229,255,0.55)' : 'rgba(255,255,255,0.09)'}`,
        boxShadow: focused ? '0 0 0 3px rgba(0,229,255,0.09), 0 0 16px rgba(0,229,255,0.06)' : 'none',
      }}
    >
      {Icon && (
        <Icon
          size={15}
          className="flex-shrink-0 transition-colors duration-200"
          style={{ color: focused ? '#00E5FF' : 'rgba(148,163,184,0.6)' }}
        />
      )}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        disabled={disabled}
        className="flex-1 py-3 bg-transparent text-sm text-white placeholder-slate-600 outline-none font-medium disabled:opacity-50"
      />
      {rightSlot}
    </div>
  );
}

function getStrength(pw) {
  if (!pw) return { level: 0, label: '', color: '' };
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  const map = [
    { label: 'Weak', color: '#FF4444' },
    { label: 'Fair', color: '#FFB020' },
    { label: 'Good', color: '#00B8D4' },
    { label: 'Strong', color: '#00E676' },
  ];
  return { level: score, ...map[Math.min(score - 1, 3)] };
}

function StrengthBar({ password }) {
  const { level, label, color } = getStrength(password);
  if (!password) return null;

  return (
    <div className="flex items-center gap-2 mt-1">
      <div className="flex gap-1 flex-1">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-1 flex-1 rounded-full transition-all duration-300"
            style={{
              background: i <= level ? color : 'rgba(255,255,255,0.08)',
              boxShadow: i <= level ? `0 0 6px ${color}60` : 'none',
            }}
          />
        ))}
      </div>
      {label && (
        <span className="text-[11px] font-semibold" style={{ color }}>
          {label}
        </span>
      )}
    </div>
  );
}

function SuccessOverlay() {
  return (
    <div className="flex flex-col items-center justify-center gap-5 py-8" style={{ animation: 'scaleIn 0.4s cubic-bezier(0.34,1.56,0.64,1)' }}>
      <div
        className="w-20 h-20 rounded-full flex items-center justify-center"
        style={{
          background: 'rgba(0,230,118,0.12)',
          border: '2px solid rgba(0,230,118,0.5)',
          boxShadow: '0 0 40px rgba(0,230,118,0.3)',
        }}
      >
        <CheckCircle size={38} className="text-emerald-400" />
      </div>
      <div className="text-center">
        <h3 className="text-xl font-black text-white mb-2">Account Created!</h3>
        <p className="text-sm text-slate-400 leading-relaxed max-w-[260px]">
          Your account is ready. Redirecting you to sign in.
        </p>
      </div>
      <div
        className="flex items-center gap-2 px-4 py-2 rounded-full"
        style={{ background: 'rgba(0,230,118,0.08)', border: '1px solid rgba(0,230,118,0.25)' }}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
        <span className="text-xs font-mono text-emerald-400 tracking-wider">Redirecting to login...</span>
      </div>
    </div>
  );
}

function validateForm(form) {
  const err = {};
  if (!form.name.trim()) err.name = 'Full name is required.';
  if (!form.email.trim()) {
    err.email = 'Email is required.';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    err.email = 'Enter a valid email address.';
  }
  if (!form.password) {
    err.password = 'Password is required.';
  } else if (form.password.length < 8) {
    err.password = 'Password must be at least 8 characters.';
  }
  if (!form.confirmPassword) {
    err.confirmPassword = 'Please confirm your password.';
  } else if (form.password !== form.confirmPassword) {
    err.confirmPassword = 'Passwords do not match.';
  }
  return err;
}

const INITIAL_FORM = {
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
};

export default function SignUpPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL_FORM);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [shake, setShake] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const err = validateForm(form);
    if (Object.keys(err).length) {
      setErrors(err);
      triggerShake();
      return;
    }

    setSubmitError('');
    setErrors({});
    setLoading(true);

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setSubmitError(data.message || 'Could not create account.');
        triggerShake();
        return;
      }

      setSuccess(true);

      setTimeout(() => {
        navigate('/login');
      }, 1800);
    } catch {
      setSubmitError('Could not reach the server. Make sure the backend is running.');
      triggerShake();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 sm:p-6 overflow-hidden" style={{ background: '#0A0F1E' }}>
      <ParticleBackground />

      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse 70% 70% at 50% 40%, rgba(0,50,120,0.18) 0%, transparent 65%), ' +
            'radial-gradient(ellipse 50% 40% at 20% 80%, rgba(255,50,50,0.04) 0%, transparent 60%)',
        }}
      />

      <div
        className="relative w-full max-w-[460px] rounded-2xl overflow-hidden"
        style={{
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.09)',
          backdropFilter: 'blur(28px)',
          WebkitBackdropFilter: 'blur(28px)',
          boxShadow: '0 30px 100px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,229,255,0.04)',
          animation: shake ? 'shake 0.45s ease' : 'slideUp 0.5s ease',
        }}
      >
        <div className="h-0.5 w-full" style={{ background: 'linear-gradient(90deg, transparent, #00E5FF, #0099FF, transparent)' }} />

        <style>{`
          @keyframes slideUp      { from { opacity:0; transform:translateY(28px); } to { opacity:1; transform:translateY(0); } }
          @keyframes fadeSlideIn  { from { opacity:0; transform:translateY(-4px); } to { opacity:1; transform:translateY(0); } }
          @keyframes shake        { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-8px)} 40%{transform:translateX(8px)} 60%{transform:translateX(-5px)} 80%{transform:translateX(5px)} }
          @keyframes scaleIn      { from { opacity:0; transform:scale(0.8); } to { opacity:1; transform:scale(1); } }
          @keyframes spin         { to { transform:rotate(360deg); } }
        `}</style>

        <div className="p-7 sm:p-9 flex flex-col gap-6">
          <div className="text-center flex flex-col items-center gap-3">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, rgba(0,229,255,0.2) 0%, rgba(0,100,200,0.15) 100%)',
                border: '1px solid rgba(0,229,255,0.35)',
                boxShadow: '0 0 30px rgba(0,229,255,0.2)',
              }}
            >
              <Shield size={26} style={{ color: '#00E5FF', filter: 'drop-shadow(0 0 8px rgba(0,229,255,0.6))' }} />
            </div>
            <div>
              <p className="text-[10px] font-mono font-bold tracking-[0.25em] text-[#00E5FF] uppercase mb-1">
                SecureSight
              </p>
              <h1 className="text-lg font-black text-white uppercase tracking-tight leading-snug">
                Create Your Secure Account
              </h1>
            </div>
          </div>

          {submitError && !success && (
            <div
              role="alert"
              className="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm text-red-400"
              style={{
                background: 'rgba(255,68,68,0.1)',
                border: '1px solid rgba(255,68,68,0.25)',
                animation: 'fadeSlideIn 0.2s ease',
              }}
            >
              <AlertCircle size={14} />
              {submitError}
            </div>
          )}

          {success ? (
            <SuccessOverlay />
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
              <Field id="signup-name" label="Full Name" error={errors.name}>
                <TextInput
                  id="signup-name"
                  value={form.name}
                  onChange={set('name')}
                  placeholder="Full Name"
                  icon={User}
                  autoComplete="name"
                  disabled={loading}
                />
              </Field>

              <Field id="signup-email" label="Email" error={errors.email}>
                <TextInput
                  id="signup-email"
                  type="email"
                  value={form.email}
                  onChange={set('email')}
                  placeholder="Email"
                  icon={Mail}
                  autoComplete="email"
                  disabled={loading}
                />
              </Field>

              <Field id="signup-password" label="Password" error={errors.password}>
                <TextInput
                  id="signup-password"
                  type={showPw ? 'text' : 'password'}
                  value={form.password}
                  onChange={set('password')}
                  placeholder="Create Password (min. 8 chars)"
                  icon={Lock}
                  autoComplete="new-password"
                  disabled={loading}
                  rightSlot={
                    <button
                      type="button"
                      id="toggle-pw"
                      aria-label={showPw ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPw((v) => !v)}
                      className="flex-shrink-0 p-1 text-slate-500 hover:text-[#00E5FF] transition-colors duration-150"
                    >
                      {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  }
                />
                <StrengthBar password={form.password} />
              </Field>

              <Field id="signup-confirm-password" label="Confirm Password" error={errors.confirmPassword}>
                <TextInput
                  id="signup-confirm-password"
                  type={showConfirm ? 'text' : 'password'}
                  value={form.confirmPassword}
                  onChange={set('confirmPassword')}
                  placeholder="Confirm Password"
                  icon={Lock}
                  autoComplete="new-password"
                  disabled={loading}
                  rightSlot={
                    <>
                      {form.confirmPassword && form.password === form.confirmPassword && (
                        <CheckCircle size={14} className="text-emerald-400 flex-shrink-0 mr-1" />
                      )}
                      <button
                        type="button"
                        id="toggle-confirm-pw"
                        aria-label={showConfirm ? 'Hide password' : 'Show password'}
                        onClick={() => setShowConfirm((v) => !v)}
                        className="flex-shrink-0 p-1 text-slate-500 hover:text-[#00E5FF] transition-colors duration-150"
                      >
                        {showConfirm ? <EyeOff size={14} /> : <Eye size={14} />}
                      </button>
                    </>
                  }
                />
              </Field>

              <button
                id="signup-submit"
                type="submit"
                disabled={loading}
                className="w-full py-3.5 mt-1 rounded-xl font-black text-sm uppercase tracking-widest flex items-center justify-center gap-2 transition-all duration-200"
                style={{
                  background: loading ? 'rgba(0,229,255,0.6)' : '#00E5FF',
                  color: '#0A0F1E',
                  boxShadow: loading ? '0 0 16px rgba(0,229,255,0.2)' : '0 0 28px rgba(0,229,255,0.4)',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} style={{ animation: 'spin 0.8s linear infinite' }} />
                    Creating Account...
                  </>
                ) : (
                  <>
                    <Shield size={15} />
                    Create Account
                  </>
                )}
              </button>

              <p className="text-center text-sm text-slate-500 pt-1">
                Already have an account?{' '}
                <a
                  href="/login"
                  id="go-to-login"
                  className="font-semibold text-[#00E5FF] hover:text-[#00B8D4] transition-colors duration-150 underline underline-offset-2 decoration-dotted"
                >
                  Sign In
                </a>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
