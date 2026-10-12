import { createElement, useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Mail, Lock, Eye, EyeOff, ArrowRight, Loader2 } from 'lucide-react';
import { saveUser } from '../utils/auth';

function CyberEye() {
  const canvasRef = useRef(null);
  const angleRef = useRef(0);
  const rafRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);

    const draw = () => {
      const W = canvas.width;
      const H = canvas.height;
      const cx = W / 2;
      const cy = H / 2;

      ctx.clearRect(0, 0, W, H);

      const hexR = 28;
      const hexH = hexR * Math.sqrt(3);
      ctx.strokeStyle = 'rgba(0,229,255,0.04)';
      ctx.lineWidth = 1;
      for (let row = -2; row < H / hexH + 2; row++) {
        for (let col = -2; col < W / (hexR * 1.5) + 2; col++) {
          const x = col * hexR * 3 + (row % 2 === 0 ? 0 : hexR * 1.5);
          const y = row * hexH;
          ctx.beginPath();
          for (let i = 0; i < 6; i++) {
            const a = (Math.PI / 180) * (60 * i - 30);
            const px = x + hexR * Math.cos(a);
            const py = y + hexR * Math.sin(a);
            i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
          }
          ctx.closePath();
          ctx.stroke();
        }
      }

      const rings = [
        { r: 205, opacity: 0.06, dash: [4, 8], width: 1, rotate: 0 },
        { r: 185, opacity: 0.1, dash: [8, 12], width: 1, rotate: 20 },
        { r: 162, opacity: 0.15, dash: [], width: 1, rotate: 0 },
        { r: 142, opacity: 0.2, dash: [3, 6], width: 1.5, rotate: 45 },
        { r: 122, opacity: 0.28, dash: [], width: 1.5, rotate: 0 },
        { r: 100, opacity: 0.35, dash: [6, 8], width: 2, rotate: 30 },
      ];

      rings.forEach(({ r, opacity, dash, width, rotate }) => {
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate((rotate * Math.PI) / 180);
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0,229,255,${opacity})`;
        ctx.lineWidth = width;
        ctx.setLineDash(dash);
        ctx.stroke();
        ctx.restore();
      });
      ctx.setLineDash([]);

      for (let i = 0; i < 72; i++) {
        const tickAngle = (i / 72) * Math.PI * 2;
        const isLong = i % 9 === 0;
        const inner = 205 - (isLong ? 10 : 5);
        ctx.beginPath();
        ctx.moveTo(cx + 205 * Math.cos(tickAngle), cy + 205 * Math.sin(tickAngle));
        ctx.lineTo(cx + inner * Math.cos(tickAngle), cy + inner * Math.sin(tickAngle));
        ctx.strokeStyle = `rgba(0,229,255,${isLong ? 0.5 : 0.2})`;
        ctx.lineWidth = isLong ? 1.5 : 0.8;
        ctx.stroke();
      }

      const irisGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 90);
      irisGrad.addColorStop(0, 'rgba(0,180,220,0.55)');
      irisGrad.addColorStop(0.35, 'rgba(0,100,170,0.45)');
      irisGrad.addColorStop(0.75, 'rgba(0,50,120,0.35)');
      irisGrad.addColorStop(1, 'rgba(0,20,60,0.2)');
      ctx.beginPath();
      ctx.arc(cx, cy, 90, 0, Math.PI * 2);
      ctx.fillStyle = irisGrad;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(cx, cy, 90, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0,229,255,0.6)';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#00E5FF';
      ctx.shadowBlur = 24;
      ctx.stroke();
      ctx.shadowBlur = 0;

      for (let i = 0; i < 24; i++) {
        const a = (i / 24) * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(cx + 30 * Math.cos(a), cy + 30 * Math.sin(a));
        ctx.lineTo(cx + 88 * Math.cos(a), cy + 88 * Math.sin(a));
        ctx.strokeStyle = 'rgba(0,229,255,0.08)';
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }

      const pupilGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 36);
      pupilGrad.addColorStop(0, '#001020');
      pupilGrad.addColorStop(0.6, '#000810');
      pupilGrad.addColorStop(1, '#000510');
      ctx.beginPath();
      ctx.arc(cx, cy, 36, 0, Math.PI * 2);
      ctx.fillStyle = pupilGrad;
      ctx.fill();
      ctx.strokeStyle = 'rgba(0,229,255,0.3)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      const spec = ctx.createRadialGradient(cx - 10, cy - 10, 0, cx - 10, cy - 10, 14);
      spec.addColorStop(0, 'rgba(0,229,255,0.5)');
      spec.addColorStop(1, 'transparent');
      ctx.beginPath();
      ctx.arc(cx - 10, cy - 10, 14, 0, Math.PI * 2);
      ctx.fillStyle = spec;
      ctx.fill();

      const dotGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 8);
      dotGrad.addColorStop(0, 'rgba(0,229,255,0.9)');
      dotGrad.addColorStop(1, 'transparent');
      ctx.beginPath();
      ctx.arc(cx, cy, 8, 0, Math.PI * 2);
      ctx.fillStyle = dotGrad;
      ctx.shadowColor = '#00E5FF';
      ctx.shadowBlur = 16;
      ctx.fill();
      ctx.shadowBlur = 0;

      angleRef.current = (angleRef.current + 0.008) % (Math.PI * 2);
      const scanA = angleRef.current;
      const scanLen = 200;
      const coneSpread = 0.18;

      ctx.save();
      ctx.translate(cx, cy);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, scanLen, scanA - coneSpread * 0.5, scanA + coneSpread * 2, false);
      ctx.closePath();
      const grad = ctx.createLinearGradient(0, 0, Math.cos(scanA) * scanLen, Math.sin(scanA) * scanLen);
      grad.addColorStop(0, 'rgba(0,229,255,0.25)');
      grad.addColorStop(0.7, 'rgba(0,229,255,0.08)');
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.restore();

      ctx.save();
      ctx.translate(cx, cy);
      ctx.beginPath();
      ctx.moveTo(35 * Math.cos(scanA), 35 * Math.sin(scanA));
      ctx.lineTo(scanLen * Math.cos(scanA), scanLen * Math.sin(scanA));
      ctx.strokeStyle = 'rgba(0,229,255,0.9)';
      ctx.lineWidth = 1.5;
      ctx.shadowColor = '#00E5FF';
      ctx.shadowBlur = 12;
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.restore();

      const now = Date.now() / 1000;
      const nodes = [0, 60, 130, 200, 280, 330];
      nodes.forEach((baseDeg, i) => {
        const a = ((baseDeg + now * (i % 2 === 0 ? 6 : -4)) * Math.PI) / 180;
        const nr = 162;
        const nx = cx + nr * Math.cos(a);
        const ny = cy + nr * Math.sin(a);
        const pulse = 0.5 + 0.5 * Math.sin(now * 3 + i);
        ctx.beginPath();
        ctx.arc(nx, ny, 3, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,229,255,${0.4 + pulse * 0.5})`;
        ctx.shadowColor = '#00E5FF';
        ctx.shadowBlur = 8 + pulse * 8;
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      const ambGrad = ctx.createRadialGradient(cx, cy, 100, cx, cy, 220);
      ambGrad.addColorStop(0, 'rgba(0,229,255,0.06)');
      ambGrad.addColorStop(1, 'transparent');
      ctx.beginPath();
      ctx.arc(cx, cy, 220, 0, Math.PI * 2);
      ctx.fillStyle = ambGrad;
      ctx.fill();

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(rafRef.current);
      ro.disconnect();
    };
  }, []);

  return <canvas ref={canvasRef} className="w-full h-full" style={{ display: 'block' }} aria-hidden="true" />;
}

function InputField({
  id,
  type,
  value,
  onChange,
  placeholder,
  icon: Icon,
  rightSlot,
  autoComplete,
}) {
  const [focused, setFocused] = useState(false);
  const iconElement = Icon
    ? createElement(Icon, {
        size: 16,
        className: 'flex-shrink-0 transition-colors duration-200',
        style: { color: focused ? '#00E5FF' : 'rgba(148,163,184,0.7)' },
      })
    : null;

  return (
    <div
      className="flex items-center gap-3 px-4 rounded-xl transition-all duration-200"
      style={{
        background: 'rgba(255,255,255,0.05)',
        border: `1px solid ${focused ? 'rgba(0,229,255,0.55)' : 'rgba(255,255,255,0.09)'}`,
        boxShadow: focused ? '0 0 0 3px rgba(0,229,255,0.10), 0 0 20px rgba(0,229,255,0.08)' : 'none',
      }}
    >
      {iconElement}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        className="flex-1 py-3.5 bg-transparent text-sm text-white placeholder-slate-500 outline-none font-medium"
      />
      {rightSlot}
    </div>
  );
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [shake, setShake] = useState(false);

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password) {
      setError('Please fill in both fields.');
      triggerShake();
      return;
    }

    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!emailOk) {
      setError('Please enter a valid email address.');
      triggerShake();
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || 'Login failed.');
        triggerShake();
        return;
      }

      saveUser(data.user);
      navigate('/dashboard');
    } catch {
      setError('Could not reach the server. Make sure the backend is running.');
      triggerShake();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex overflow-hidden" style={{ background: '#0A0F1E' }}>
      <div className="hidden lg:flex flex-col relative w-1/2 overflow-hidden">
        <div
          className="absolute inset-0"
          style={{
            background:
              'radial-gradient(ellipse 70% 70% at 50% 50%, rgba(0,60,120,0.35) 0%, rgba(0,20,60,0.2) 50%, #06091a 100%)',
          }}
        />

        <div className="absolute inset-0">
          <CyberEye />
        </div>

        <div className="relative z-10 p-8 flex items-center gap-2.5">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{
              background: 'rgba(0,229,255,0.12)',
              border: '1px solid rgba(0,229,255,0.35)',
              boxShadow: '0 0 15px rgba(0,229,255,0.2)',
            }}
          >
            <Shield size={18} className="text-[#00E5FF]" />
          </div>
          <span className="text-lg font-bold tracking-tight">
            <span className="text-white">Secure</span>
            <span className="text-[#00E5FF]">Sight</span>
          </span>
        </div>
      </div>

      <div className="flex-1 lg:w-1/2 flex items-center justify-center p-6 sm:p-10 relative">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background: 'radial-gradient(ellipse 60% 50% at 50% 50%, rgba(0,229,255,0.04) 0%, transparent 70%)',
          }}
        />

        <div className="lg:hidden absolute top-6 left-6 flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{
              background: 'rgba(0,229,255,0.12)',
              border: '1px solid rgba(0,229,255,0.3)',
            }}
          >
            <Shield size={15} className="text-[#00E5FF]" />
          </div>
          <span className="text-base font-bold">
            <span className="text-white">Secure</span>
            <span className="text-[#00E5FF]">Sight</span>
          </span>
        </div>

        <div
          className="relative w-full max-w-[420px]"
          style={{
            animation: `${shake ? 'shake 0.45s ease' : 'slideUp 0.5s ease'}`,
          }}
        >
          <style>{`
            @keyframes slideUp {
              from { opacity: 0; transform: translateY(24px); }
              to   { opacity: 1; transform: translateY(0); }
            }
            @keyframes shake {
              0%,100% { transform: translateX(0); }
              20%     { transform: translateX(-8px); }
              40%     { transform: translateX(8px); }
              60%     { transform: translateX(-5px); }
              80%     { transform: translateX(5px); }
            }
            @keyframes fadeIn {
              from { opacity: 0; }
              to   { opacity: 1; }
            }
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `}</style>

          <div
            className="rounded-2xl p-8 sm:p-10 flex flex-col gap-7"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.09)',
              backdropFilter: 'blur(24px)',
              WebkitBackdropFilter: 'blur(24px)',
              boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
            }}
          >
            <div className="text-center flex flex-col items-center gap-4">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center"
                style={{
                  background: 'rgba(0,229,255,0.1)',
                  border: '1px solid rgba(0,229,255,0.3)',
                  boxShadow: '0 0 24px rgba(0,229,255,0.2)',
                }}
              >
                <Shield size={26} className="text-[#00E5FF]" />
              </div>
              <div>
                <h2 className="text-2xl font-black text-white tracking-tight">Welcome Back</h2>
                <p className="text-sm text-slate-400 mt-1">Sign in with your registered email and password</p>
              </div>
            </div>

            {error && (
              <div
                role="alert"
                className="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm text-red-400"
                style={{
                  background: 'rgba(255,68,68,0.1)',
                  border: '1px solid rgba(255,68,68,0.25)',
                  animation: 'fadeIn 0.3s ease',
                }}
              >
                <span className="text-red-400">!</span>
                {error}
              </div>
            )}

            <form onSubmit={handleLogin} className="flex flex-col gap-4" noValidate>
              <div className="flex flex-col gap-1.5">
                <label htmlFor="login-email" className="text-xs font-semibold text-slate-400 tracking-wide uppercase">
                  Email Address
                </label>
                <InputField
                  id="login-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  icon={Mail}
                  autoComplete="email"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="login-password" className="text-xs font-semibold text-slate-400 tracking-wide uppercase">
                  Password
                </label>
                <InputField
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  icon={Lock}
                  autoComplete="current-password"
                  rightSlot={
                    <button
                      type="button"
                      id="toggle-password"
                      onClick={() => setShowPassword((v) => !v)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      className="flex-shrink-0 p-1 rounded-md text-slate-500 hover:text-[#00E5FF] transition-colors duration-150"
                    >
                      {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  }
                />
              </div>

              <button
                id="login-submit"
                type="submit"
                disabled={isLoading}
                className="mt-1 w-full py-3.5 rounded-xl font-bold text-sm uppercase tracking-widest text-navy transition-all duration-200 flex items-center justify-center gap-2"
                style={{
                  background: isLoading ? 'rgba(0,229,255,0.6)' : '#00E5FF',
                  boxShadow: isLoading ? '0 0 20px rgba(0,229,255,0.25)' : '0 0 28px rgba(0,229,255,0.45)',
                  color: '#0A0F1E',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                }}
                onMouseEnter={(e) => {
                  if (!isLoading) e.currentTarget.style.boxShadow = '0 0 45px rgba(0,229,255,0.7)';
                }}
                onMouseLeave={(e) => {
                  if (!isLoading) e.currentTarget.style.boxShadow = '0 0 28px rgba(0,229,255,0.45)';
                }}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} style={{ animation: 'spin 0.8s linear infinite' }} />
                    Authenticating...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight size={15} />
                  </>
                )}
              </button>
            </form>

            <p className="text-center text-sm text-slate-500">
              Don't have an account?{' '}
              <a
                href="/signup"
                id="go-to-signup"
                className="font-semibold text-[#00E5FF] hover:text-[#00B8D4] transition-colors duration-150 underline underline-offset-2 decoration-dotted"
              >
                Sign Up
              </a>
            </p>
          </div>
        </div>
      </div>

      <div
        className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-px pointer-events-none"
        style={{
          background: 'linear-gradient(to bottom, transparent, rgba(0,229,255,0.2) 30%, rgba(0,229,255,0.2) 70%, transparent)',
        }}
      />
    </div>
  );
}
