import process from 'node:process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import mqtt from 'mqtt';
import { mqttConfig } from './config.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaultQueueFile = path.join(__dirname, 'offline-alerts', 'queue.ndjson');
const queueFile = mqttConfig.offlineQueueFile || defaultQueueFile;
const NORMAL_LABEL = 'Normal';
const alertCooldownMs = 30_000;
const recentAlerts = new Map();

let client = null;
let connected = false;
let flushing = false;

const roleRoutes = {
  Theft: ['police'],
  Arrest: ['police'],
  Shooting: ['police'],
  Vandalism: ['police'],
  'Physical Violence': ['police', 'hospital'],
  RoadAccidents: ['hospital', 'police'],
  Arson: ['firefighters', 'police'],
  Explosion: ['firefighters', 'hospital', 'police'],
};

const ensureQueueDir = async () => {
  await fs.promises.mkdir(path.dirname(queueFile), { recursive: true });
};

const appendQueuedAlert = async (record) => {
  await ensureQueueDir();
  await fs.promises.appendFile(queueFile, `${JSON.stringify(record)}\n`, 'utf8');
};

const queueAlertRecord = async (record) => {
  try {
    await appendQueuedAlert(record);
  } catch (error) {
    console.error('MQTT offline queue write failed:', error.message);
  }
};

const readQueuedAlerts = async () => {
  try {
    const content = await fs.promises.readFile(queueFile, 'utf8');
    return content
      .split(/\r?\n/)
      .filter(Boolean)
      .map((line) => JSON.parse(line));
  } catch (error) {
    if (error.code === 'ENOENT') return [];
    throw error;
  }
};

const replaceQueue = async (records) => {
  await ensureQueueDir();
  if (!records.length) {
    await fs.promises.rm(queueFile, { force: true });
    return;
  }

  await fs.promises.writeFile(
    queueFile,
    records.map((record) => JSON.stringify(record)).join('\n') + '\n',
    'utf8',
  );
};

const publishMqtt = (topic, payload) =>
  new Promise((resolve, reject) => {
    if (!client || !connected) {
      reject(new Error('MQTT broker is offline.'));
      return;
    }

    client.publish(topic, JSON.stringify(payload), { qos: mqttConfig.publishQos }, (error) => {
      if (error) reject(error);
      else resolve();
    });
  });

const topicsForRoles = (roles) => roles.map((role) => `${mqttConfig.topicPrefix}/${role}`);

const flushQueuedAlerts = async () => {
  if (!mqttConfig.enabled || !connected || flushing) return;
  flushing = true;

  try {
    const queued = await readQueuedAlerts();
    const remaining = [];

    for (const record of queued) {
      try {
        await publishMqtt(record.topic, record.payload);
      } catch {
        remaining.push(record);
      }
    }

    await replaceQueue(remaining);
    if (queued.length && !remaining.length) {
      console.log(`MQTT offline alert queue flushed (${queued.length} payloads).`);
    }
  } catch (error) {
    console.error('MQTT offline queue flush failed:', error.message);
  } finally {
    flushing = false;
  }
};

export const startAlertBroker = () => {
  if (!mqttConfig.enabled || client) return;

  client = mqtt.connect(mqttConfig.url, {
    clientId: mqttConfig.clientId,
    username: mqttConfig.username || undefined,
    password: mqttConfig.password || undefined,
    clean: false,
    reconnectPeriod: 5000,
    connectTimeout: 5000,
  });

  client.on('connect', () => {
    connected = true;
    console.log(`MQTT alert broker connected: ${mqttConfig.url}`);
    flushQueuedAlerts();
  });

  client.on('offline', () => {
    connected = false;
  });

  client.on('close', () => {
    connected = false;
  });

  client.on('error', (error) => {
    connected = false;
    console.error('MQTT alert broker error:', error.message);
  });
};

const shouldPublishAlert = (payload) => {
  const key = `${payload.sourceUrl}:${payload.eventType}`;
  const lastPublishedAt = recentAlerts.get(key) || 0;

  if (Date.now() - lastPublishedAt < alertCooldownMs) {
    return false;
  }

  recentAlerts.set(key, Date.now());
  return true;
};

export const buildAlertPayload = ({ prediction, sourceUrl, sourceLabel, timestamp }) => {
  const threshold = prediction.threshold ?? 0.7;
  const confidence = prediction.probability ?? 0;
  const eventType = prediction.rawLabel || prediction.label || NORMAL_LABEL;

  if (eventType === NORMAL_LABEL || confidence < threshold) {
    return null;
  }

  const roles = roleRoutes[eventType] || ['police'];
  return {
    id: crypto.randomUUID(),
    eventType,
    confidence,
    threshold,
    severity: confidence >= 0.9 ? 'critical' : 'high',
    sourceUrl,
    sourceLabel,
    videoTimestamp: Number(timestamp) || 0,
    windowStart: prediction.windowStart ?? (Number(timestamp) || 0),
    roles,
    createdAt: new Date().toISOString(),
    edgeNode: mqttConfig.clientId,
  };
};

export const publishAlert = async (payload) => {
  if (!mqttConfig.enabled || !payload || !shouldPublishAlert(payload)) return;

  const records = topicsForRoles([...new Set([...payload.roles, 'admin'])]).map((topic) => ({
    topic,
    payload,
    queuedAt: new Date().toISOString(),
  }));

  for (const record of records) {
    try {
      await publishMqtt(record.topic, record.payload);
    } catch {
      await queueAlertRecord(record);
    }
  }

  if (!connected) {
    console.log(`MQTT offline. Alert queued locally: ${payload.eventType}`);
  }
};

process.on('beforeExit', () => {
  if (client) client.end(true);
});
