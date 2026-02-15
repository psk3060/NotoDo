interface EnvConfig {
  IS_DEV : boolean;
  API_BASE_URL : string;
}

const mode = import.meta.env.MODE;

export const ENV = {
  IS_DEV : mode === 'dev',
  API_BASE_URL : import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
} as EnvConfig;
