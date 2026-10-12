import process from 'node:process';

const readEnv = (key, fallback) => (process.env[key] === undefined ? fallback : process.env[key]);

export const dbConfig = {
  host: readEnv('DB_HOST', 'localhost'),
  port: Number(readEnv('DB_PORT', 3306)),
  user: readEnv('DB_USER', 'root'),
  password: readEnv('DB_PASSWORD', ''),
  database: readEnv('DB_NAME', 'securesight_database'),
};

export const serverConfig = {
  port: Number(readEnv('PORT', 4000)),
};

export const mqttConfig = {
  enabled: readEnv('MQTT_ENABLED', 'true') !== 'false',
  url: readEnv('MQTT_URL', 'mqtt://127.0.0.1:1883'),
  username: readEnv('MQTT_USERNAME', ''),
  password: readEnv('MQTT_PASSWORD', ''),
  clientId: readEnv('MQTT_CLIENT_ID', `securesight-edge-${process.pid}`),
  topicPrefix: readEnv('MQTT_TOPIC_PREFIX', 'securesight/alerts'),
  offlineQueueFile: readEnv('MQTT_OFFLINE_QUEUE_FILE', ''),
  publishQos: Number(readEnv('MQTT_QOS', 1)),
};
