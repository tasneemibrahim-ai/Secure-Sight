import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  Camera,
  CheckCircle2,
  Clapperboard,
  Link,
  LogOut,
  Play,
  Radio,
  Shield,
  Video,
} from 'lucide-react';
import { clearUser, getUser } from '../utils/auth';

const DEFAULT_CAMERA = {
  name: '',
  streamUrl: '',
};
const DEFAULT_PREDICTION = {
  label: 'Normal',
  rawLabel: 'Normal',
  probability: 1,
  threshold: 0.7,
};
const STABLE_CONFIRMATION_MS = 5000;

function getStorageKey(userId) {
  return `securesight_camera_${userId}`;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const user = getUser();
  const videoRef = useRef(null);
  const inFlightRef = useRef(false);
  const candidateRef = useRef(null);
  const declaredPredictionRef = useRef(DEFAULT_PREDICTION);
  const candidateTimeoutRef = useRef(null);
  const requestVersionRef = useRef(0);
  const [mode, setMode] = useState('demo');
  const [camera, setCamera] = useState(DEFAULT_CAMERA);
  const [cameraDraft, setCameraDraft] = useState(DEFAULT_CAMERA);
  const [demoVideos, setDemoVideos] = useState([]);
  const [selectedDemo, setSelectedDemo] = useState('');
  const [loadingVideos, setLoadingVideos] = useState(true);
  const [videoError, setVideoError] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [rawPrediction, setRawPrediction] = useState(DEFAULT_PREDICTION);
  const [declaredPrediction, setDeclaredPrediction] = useState(DEFAULT_PREDICTION);
  const [candidateLabel, setCandidateLabel] = useState('');
  const [inferenceStatus, setInferenceStatus] = useState('idle');
  const [inferenceError, setInferenceError] = useState('');
  const [analysisRunKey, setAnalysisRunKey] = useState(0);

  const resetClassificationState = useCallback((nextStatus = 'ready') => {
    window.clearTimeout(candidateTimeoutRef.current);
    candidateTimeoutRef.current = null;
    candidateRef.current = null;
    declaredPredictionRef.current = DEFAULT_PREDICTION;
    setRawPrediction(DEFAULT_PREDICTION);
    setDeclaredPrediction(DEFAULT_PREDICTION);
    setCandidateLabel('');
    setInferenceStatus(nextStatus);
    setInferenceError('');
  }, []);

  useEffect(() => {
    if (!user) return;
    const savedCamera = localStorage.getItem(getStorageKey(user.id));
    if (!savedCamera) return;

    try {
      const parsed = JSON.parse(savedCamera);
      setCamera({ ...DEFAULT_CAMERA, ...parsed });
      setCameraDraft({ ...DEFAULT_CAMERA, ...parsed });
    } catch {
      localStorage.removeItem(getStorageKey(user.id));
    }
  }, [user]);

  useEffect(() => {
    let active = true;

    const loadDemoVideos = async () => {
      try {
        const response = await fetch('/api/demo-videos');
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || 'Could not load demo videos.');
        }

        if (!active) return;
        setDemoVideos(data.videos || []);
        setSelectedDemo((current) => current || data.videos?.[0]?.url || '');
      } catch (error) {
        if (active) setVideoError(error.message);
      } finally {
        if (active) setLoadingVideos(false);
      }
    };

    loadDemoVideos();
    return () => {
      active = false;
    };
  }, []);

  const activeSource = useMemo(() => {
    if (mode === 'camera') {
      return {
        label: camera.name || 'Linked camera',
        url: camera.streamUrl,
        type: 'camera',
      };
    }

    const video = demoVideos.find((item) => item.url === selectedDemo);
    return {
      label: video?.name || 'Demo video',
      url: selectedDemo,
      type: 'demo',
    };
  }, [camera, demoVideos, mode, selectedDemo]);

  useEffect(() => {
    requestVersionRef.current += 1;
    inFlightRef.current = false;
    resetClassificationState(activeSource.url ? 'ready' : 'idle');
    setIsPlaying(false);
  }, [activeSource.url, resetClassificationState]);

  const handleVideoSeek = () => {
    requestVersionRef.current += 1;
    inFlightRef.current = false;
    resetClassificationState(isPlaying ? 'running' : 'ready');
    setAnalysisRunKey((current) => current + 1);
  };

  useEffect(() => {
    if (!activeSource.url || !isPlaying) return undefined;

    let cancelled = false;
    const clearCandidate = () => {
      window.clearTimeout(candidateTimeoutRef.current);
      candidateTimeoutRef.current = null;
      candidateRef.current = null;
      setCandidateLabel('');
    };

    const promoteCandidate = () => {
      const candidate = candidateRef.current;
      if (!candidate || cancelled) return;

      declaredPredictionRef.current = candidate.prediction;
      setDeclaredPrediction(candidate.prediction);
      clearCandidate();
    };

    const applyStablePrediction = (prediction) => {
      const threshold = prediction.threshold ?? DEFAULT_PREDICTION.threshold;
      const probability = prediction.probability ?? 0;
      const rawLabel = prediction.rawLabel || prediction.label || 'Normal';
      const nextLabel = probability >= threshold ? rawLabel : 'Normal';
      const normalizedPrediction = { ...prediction, label: nextLabel, rawLabel };
      const activeDeclared = declaredPredictionRef.current;

      if (nextLabel === activeDeclared.label) {
        clearCandidate();
        return;
      }

      const now = Date.now();
      const candidate = candidateRef.current;
      if (!candidate || candidate.label !== nextLabel) {
        candidateRef.current = { label: nextLabel, since: now, prediction: normalizedPrediction };
        setCandidateLabel(nextLabel);
        window.clearTimeout(candidateTimeoutRef.current);
        candidateTimeoutRef.current = window.setTimeout(promoteCandidate, STABLE_CONFIRMATION_MS);
        return;
      }

      candidateRef.current = { ...candidate, prediction: normalizedPrediction };
      if (now - candidate.since >= STABLE_CONFIRMATION_MS) {
        promoteCandidate();
      }
    };

    const classifyFrameWindow = async () => {
      if (inFlightRef.current || !videoRef.current) return;
      const requestVersion = requestVersionRef.current;
      const requestedTimestamp = videoRef.current.currentTime || 0;
      inFlightRef.current = true;
      setInferenceStatus((current) => (current === 'connected' ? 'connected' : 'running'));

      try {
        const response = await fetch('/api/classify-video', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sourceUrl: activeSource.url,
            timestamp: requestedTimestamp,
          }),
        });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || 'Could not classify video.');
        }

        if (cancelled || requestVersion !== requestVersionRef.current) return;
        setRawPrediction(data);
        setInferenceStatus('connected');
        setInferenceError('');
        applyStablePrediction(data);
      } catch (error) {
        if (!cancelled) {
          setInferenceStatus('error');
          setInferenceError(error.message);
        }
      } finally {
        inFlightRef.current = false;
      }
    };

    classifyFrameWindow();
    const intervalId = window.setInterval(classifyFrameWindow, 2000);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
      window.clearTimeout(candidateTimeoutRef.current);
    };
  }, [activeSource.url, analysisRunKey, isPlaying]);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleLogout = () => {
    clearUser();
    navigate('/login');
  };

  const handleCameraSave = (event) => {
    event.preventDefault();
    const nextCamera = {
      name: cameraDraft.name.trim(),
      streamUrl: cameraDraft.streamUrl.trim(),
    };

    setCamera(nextCamera);
    localStorage.setItem(getStorageKey(user.id), JSON.stringify(nextCamera));
    setMode('camera');
  };

  return (
    <div className="min-h-screen bg-navy text-white">
      <div className="max-content px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-[#00E5FF]/10 border border-[#00E5FF]/30">
              <Shield className="text-[#00E5FF]" size={28} />
            </div>
            <div>
              <p className="text-xs font-mono tracking-[0.2em] uppercase text-[#00E5FF]">SecureSight Dashboard</p>
              <h1 className="text-2xl sm:text-3xl font-black">Welcome, {user.name}</h1>
            </div>
          </div>

          <button type="button" onClick={handleLogout} className="btn-outline inline-flex items-center justify-center gap-2 text-sm">
            <LogOut size={16} />
            Logout
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <section className="glass rounded-2xl border border-white/10 overflow-hidden">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between px-5 py-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-[#00E5FF]/10 border border-[#00E5FF]/25">
                  {activeSource.type === 'demo' ? <Clapperboard size={18} className="text-[#00E5FF]" /> : <Camera size={18} className="text-[#00E5FF]" />}
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Active Source</p>
                  <h2 className="font-bold text-white break-all">{activeSource.label}</h2>
                </div>
              </div>

              <div className="flex rounded-xl overflow-hidden border border-white/10 bg-white/[0.03]">
                <button
                  type="button"
                  onClick={() => setMode('demo')}
                  className={`px-4 py-2 text-sm font-semibold transition-colors ${mode === 'demo' ? 'bg-[#00E5FF] text-navy' : 'text-slate-300 hover:text-white'}`}
                >
                  Demo
                </button>
                <button
                  type="button"
                  onClick={() => setMode('camera')}
                  className={`px-4 py-2 text-sm font-semibold transition-colors ${mode === 'camera' ? 'bg-[#00E5FF] text-navy' : 'text-slate-300 hover:text-white'}`}
                >
                  Camera
                </button>
              </div>
            </div>

            <div className="relative bg-black aspect-video">
              {activeSource.url ? (
                <video
                  ref={videoRef}
                  key={activeSource.url}
                  src={activeSource.url}
                  className="w-full h-full object-contain"
                  controls
                  muted
                  playsInline
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onEnded={() => setIsPlaying(false)}
                  onSeeking={handleVideoSeek}
                  onSeeked={handleVideoSeek}
                />
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-center px-6">
                  <Video size={42} className="text-[#00E5FF]" />
                  <p className="text-lg font-bold text-white">No video source selected</p>
                  <p className="text-sm text-slate-500 max-w-md">
                    Add a browser-playable camera URL or place a demo video inside the test video folder.
                  </p>
                </div>
              )}
            </div>

            <div className="grid gap-4 sm:grid-cols-3 px-5 py-4 border-t border-white/10">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <CheckCircle2 size={16} className={activeSource.url ? 'text-emerald-400' : 'text-slate-500'} />
                {activeSource.url ? 'Source ready' : 'Source needed'}
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <Radio size={16} className="text-[#00E5FF]" />
                Stream preview
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <Play
                  size={16}
                  className={inferenceStatus === 'error' ? 'text-red-400' : inferenceStatus === 'idle' ? 'text-amber-300' : 'text-emerald-400'}
                />
                {inferenceStatus === 'error'
                  ? 'AI model error'
                  : inferenceStatus === 'idle'
                    ? 'AI model ready'
                    : inferenceStatus === 'running'
                      ? 'AI model checking'
                      : 'AI model connected'}
              </div>
            </div>
          </section>

          <aside className="flex flex-col gap-6">
            <section className="glass rounded-2xl p-5 border border-white/10">
              <div className="flex items-center justify-between gap-3 mb-5">
                <div className="flex items-center gap-3">
                  <Activity size={19} className="text-[#00E5FF]" />
                  <h2 className="text-lg font-bold">Live Classification</h2>
                </div>
                <span className={`text-xs font-bold uppercase tracking-wider ${isPlaying ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {isPlaying ? 'Running' : 'Paused'}
                </span>
              </div>

              <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs text-slate-500 uppercase tracking-wider">Detected Class</p>
                <p className={`mt-2 text-2xl font-black ${declaredPrediction.label === 'Normal' ? 'text-emerald-300' : 'text-amber-300'}`}>
                  {declaredPrediction.label}
                </p>
                {(() => {
                  const isNormal = (rawPrediction.rawLabel || rawPrediction.label) === 'Normal';
                  const anomalyPct = Math.round((rawPrediction.probability || 0) * 100);
                  const normalPct = isNormal ? 100 : (100 - anomalyPct);
                  return (
                    <>
                      <div className="mt-4 h-2 rounded-full bg-white/10 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-[#00E5FF] transition-all duration-300"
                          style={{ width: `${normalPct}%` }}
                        />
                      </div>
                      <p className="mt-2 text-sm text-slate-400">
                        {isNormal
                          ? 'Normal 100%'
                          : `Normal ${normalPct}% · ${rawPrediction.rawLabel || rawPrediction.label} ${anomalyPct}%`}
                      </p>
                    </>
                  );
                })()}
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Raw Model</p>
                  <p className="mt-1 font-semibold text-white">{rawPrediction.rawLabel || rawPrediction.label}</p>
                  <p className="text-slate-500">{Math.round((rawPrediction.probability || 0) * 100)}%</p>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Rule</p>
                  <p className="mt-1 font-semibold text-white">70% min</p>
                  <p className="text-slate-500">5s stable</p>
                </div>
              </div>

              {candidateLabel && (
                <p className="mt-4 flex items-center gap-2 text-sm text-amber-300">
                  <AlertTriangle size={15} />
                  Watching {candidateLabel} for 5 seconds before changing class.
                </p>
              )}
              {inferenceError && <p className="mt-4 text-sm text-red-400">{inferenceError}</p>}
            </section>

            <section className="glass rounded-2xl p-5 border border-white/10">
              <div className="flex items-center gap-3 mb-5">
                <Clapperboard size={19} className="text-[#00E5FF]" />
                <h2 className="text-lg font-bold">Demo Mode</h2>
              </div>

              {loadingVideos ? (
                <p className="text-sm text-slate-500">Loading demo videos...</p>
              ) : demoVideos.length ? (
                <div className="flex flex-col gap-3">
                  <label htmlFor="demo-video" className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Test Video
                  </label>
                  <select
                    id="demo-video"
                    value={selectedDemo}
                    onChange={(event) => {
                      setSelectedDemo(event.target.value);
                      setMode('demo');
                    }}
                    className="w-full rounded-xl px-3 py-3 bg-white/5 border border-white/10 text-sm text-white outline-none focus:border-[#00E5FF]/60"
                  >
                    {demoVideos.map((video) => (
                      <option key={video.url} value={video.url} className="bg-[#0A0F1E]">
                        {video.name}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <p className="text-sm text-slate-500 leading-relaxed">
                  No demo videos found. Put `.mp4`, `.webm`, `.ogg`, `.mov`, or `.m4v` files in `test_videos`.
                </p>
              )}

              {videoError && <p className="mt-3 text-sm text-red-400">{videoError}</p>}
            </section>

            <section className="glass rounded-2xl p-5 border border-white/10">
              <div className="flex items-center gap-3 mb-5">
                <Link size={19} className="text-[#00E5FF]" />
                <h2 className="text-lg font-bold">Camera Link</h2>
              </div>

              <form onSubmit={handleCameraSave} className="flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="camera-name" className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Camera Name
                  </label>
                  <input
                    id="camera-name"
                    value={cameraDraft.name}
                    onChange={(event) => setCameraDraft((current) => ({ ...current, name: event.target.value }))}
                    
                    className="rounded-xl px-3 py-3 bg-white/5 border border-white/10 text-sm text-white placeholder-slate-600 outline-none focus:border-[#00E5FF]/60"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label htmlFor="camera-url" className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Stream URL
                  </label>
                  <input
                    id="camera-url"
                    value={cameraDraft.streamUrl}
                    onChange={(event) => setCameraDraft((current) => ({ ...current, streamUrl: event.target.value }))}
                    
                    className="rounded-xl px-3 py-3 bg-white/5 border border-white/10 text-sm text-white placeholder-slate-600 outline-none focus:border-[#00E5FF]/60"
                  />
                </div>

                <button
                  type="submit"
                  className="btn-cyan inline-flex items-center justify-center gap-2 text-sm"
                >
                  <Camera size={16} />
                  Link Camera
                </button>
              </form>
            </section>

            
          </aside>
        </div>
      </div>
    </div>
  );
}
