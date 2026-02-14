export const ENV = {
  PROFILE: import.meta.env.MODE ?? 'dev',
  IS_DEV: (import.meta.env.MODE ?? 'dev') === 'dev',
  IS_PROD: (import.meta.env.MODE ?? 'dev') === 'prod',
} as const;
