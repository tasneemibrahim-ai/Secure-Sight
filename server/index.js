import process from 'node:process';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import cors from 'cors';
import express from 'express';
import { buildAlertPayload, publishAlert, startAlertBroker } from './alertBroker.js';
import pool, { initDatabase } from './db.js';
import { serverConfig } from './config.js';

const app = express();
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');
const demoVideosDir = path.join(projectRoot, 'test_videos');
const inferenceScript = path.join(projectRoot, 'Model', 'inference.py');
const videoExtensions = new Set(['.mp4', '.webm', '.ogg', '.mov', '.m4v']);
const inferenceCache = new Map();
const inferenceCacheTtlMs = 30_000;
const modelApiUrl = process.env.MODEL_API_URL || 'http://127.0.0.1:5055/classify';
let databaseReady = false;

app.use(cors());
app.use(express.json());
app.use('/demo-videos', express.static(demoVideosDir));

app.get('/api/health', async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    databaseReady = true;
    res.json({ ok: true });
  } catch {
    databaseReady = false;
    res.status(500).json({ ok: false, message: 'Database connection failed.' });
  }
});

app.get('/api/demo-videos', async (_req, res) => {
  try {
    await fs.promises.mkdir(demoVideosDir, { recursive: true });
    const entries = await fs.promises.readdir(demoVideosDir, { withFileTypes: true });
    const videos = entries
      .filter((entry) => entry.isFile() && videoExtensions.has(path.extname(entry.name).toLowerCase()))
      .map((entry) => ({
        name: entry.name,
        url: `/demo-videos/${encodeURIComponent(entry.name)}`,
      }));

    return res.json({ videos });
  } catch (error) {
    console.error('Demo videos error:', error);
    return res.status(500).json({ message: 'Could not read demo videos.' });
  }
});

const resolveVideoSource = (sourceUrl) => {
  if (!sourceUrl || typeof sourceUrl !== 'string') {
    throw new Error('Video source is required.');
  }

  if (/^https?:\/\//i.test(sourceUrl) || /^rtsp:\/\//i.test(sourceUrl)) {
    return sourceUrl;
  }

  const normalizedUrl = sourceUrl.startsWith('/demo-videos/')
    ? sourceUrl.replace('/demo-videos/', '')
    : sourceUrl;
  const videoName = decodeURIComponent(normalizedUrl).replace(/^[/\\]+/, '');
  const videoPath = path.resolve(demoVideosDir, videoName);

  if (!videoPath.startsWith(demoVideosDir + path.sep)) {
    throw new Error('Invalid demo video path.');
  }

  if (!videoExtensions.has(path.extname(videoPath).toLowerCase())) {
    throw new Error('Unsupported video file type.');
  }

  return videoPath;
};

const displaySourceName = (sourceUrl) => {
  if (!sourceUrl || typeof sourceUrl !== 'string') return 'Unknown source';
  if (/^https?:\/\//i.test(sourceUrl) || /^rtsp:\/\//i.test(sourceUrl)) return sourceUrl;

  const normalizedUrl = sourceUrl.startsWith('/demo-videos/')
    ? sourceUrl.replace('/demo-videos/', '')
    : sourceUrl;

  return decodeURIComponent(normalizedUrl).replace(/^[/\\]+/, '') || 'Demo video';
};

const runInference = ({ sourceUrl, timestamp }) =>
  new Promise((resolve, reject) => {
    const source = resolveVideoSource(sourceUrl);
    const runWithPythonProcess = () => {
      const args = [
        inferenceScript,
        '--video',
        source,
        '--timestamp',
        String(Math.max(0, Number(timestamp) || 0)),
        '--window-seconds',
        '5',
      ];
      const python = spawn(process.env.PYTHON || 'python', args, {
        cwd: projectRoot,
        windowsHide: true,
      });
      let stdout = '';
      let stderr = '';

      python.stdout.on('data', (chunk) => {
        stdout += chunk.toString();
      });

      python.stderr.on('data', (chunk) => {
        stderr += chunk.toString();
      });

      python.on('error', reject);
      python.on('close', (code) => {
        const output = stdout.trim().split(/\r?\n/).at(-1);
        if (code !== 0) {
          reject(new Error(output || stderr || 'Model inference failed.'));
          return;
        }

        try {
          resolve(JSON.parse(output));
        } catch {
          reject(new Error('Model inference returned invalid JSON.'));
        }
      });
    };

    fetch(modelApiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video: source,
        timestamp: Math.max(0, Number(timestamp) || 0),
        windowSeconds: 5,
      }),
    })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) {
          const error = new Error(data.error || data.message || 'Model service inference failed.');
          error.fromModelService = true;
          throw error;
        }
        resolve(data);
      })
      .catch((error) => {
        if (error.fromModelService) {
          reject(error);
          return;
        }
        runWithPythonProcess();
      });
  });

app.post('/api/classify-video', async (req, res) => {
  const { sourceUrl, timestamp = 0 } = req.body;
  const normalizedTimestamp = Math.max(0, Number(timestamp) || 0);
  const windowStart = Math.floor(normalizedTimestamp / 5) * 5;
  const cacheKey = `${sourceUrl}:${windowStart}`;
  const cached = inferenceCache.get(cacheKey);

  if (cached && Date.now() - cached.createdAt < inferenceCacheTtlMs) {
    return res.json(cached.result);
  }

  try {
    const prediction = await runInference({ sourceUrl, timestamp: windowStart });
    const result = {
      ...prediction,
      windowStart,
      stableSeconds: 5,
    };
    inferenceCache.set(cacheKey, { createdAt: Date.now(), result });
    await publishAlert(buildAlertPayload({
      prediction: result,
      sourceUrl,
      sourceLabel: displaySourceName(sourceUrl),
      timestamp: normalizedTimestamp,
    }));
    return res.json(result);
  } catch (error) {
    console.error('Classification error:', error);
    return res.status(500).json({
      message: error.message || 'Could not classify video.',
      label: 'Normal',
      rawLabel: 'Normal',
      probability: 1,
      threshold: 0.7,
      stableSeconds: 5,
    });
  }
});

app.post('/api/register', async (req, res) => {
  const { name, email, password, orgName = '', orgType = '', phone = '', location = '' } = req.body;

  if (!databaseReady) {
    return res.status(503).json({ message: 'Database is not available.' });
  }

  if (!name || !email || !password) {
    return res.status(400).json({ message: 'Name, email, and password are required.' });
  }

  try {
    const normalizedEmail = email.trim().toLowerCase();
    const [existingRows] = await pool.query(
      'SELECT id FROM users WHERE email = ? LIMIT 1',
      [normalizedEmail]
    );

    if (existingRows.length > 0) {
      return res.status(409).json({ message: 'An account with this email already exists.' });
    }

    const [result] = await pool.query(
      `INSERT INTO users (name, email, password, org_name, org_type, phone, location)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        name.trim(),
        normalizedEmail,
        password,
        orgName.trim(),
        orgType.trim(),
        phone.trim(),
        location.trim(),
      ]
    );

    return res.status(201).json({
      message: 'Account created successfully.',
      user: {
        id: result.insertId,
        name: name.trim(),
        email: normalizedEmail,
        orgName: orgName.trim(),
        orgType: orgType.trim(),
        phone: phone.trim(),
        location: location.trim(),
      },
    });
  } catch (error) {
    console.error('Register error:', error);
    return res.status(500).json({ message: 'Could not create account.' });
  }
});

app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;

  if (!databaseReady) {
    return res.status(503).json({ message: 'Database is not available.' });
  }

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required.' });
  }

  try {
    const [rows] = await pool.query(
      `SELECT id, name, email, password, org_name AS orgName, org_type AS orgType, phone, location
       FROM users
       WHERE email = ?
       LIMIT 1`,
      [email.trim().toLowerCase()]
    );

    if (rows.length === 0 || rows[0].password !== password) {
      return res.status(401).json({ message: 'Invalid email or password.' });
    }

    const user = rows[0];
    delete user.password;

    return res.json({
      message: 'Login successful.',
      user,
    });
  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).json({ message: 'Could not log in.' });
  }
});

const start = async () => {
  try {
    await initDatabase();
    databaseReady = true;
  } catch (error) {
    databaseReady = false;
    console.error('Database unavailable. Auth endpoints are disabled until MySQL is running:', error.message);
  }

  app.listen(serverConfig.port, () => {
    console.log(`SecureSight API running on http://127.0.0.1:${serverConfig.port}`);
  });
  startAlertBroker();
};

start();
