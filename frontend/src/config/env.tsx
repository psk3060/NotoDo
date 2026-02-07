export const ENV = {
  PROFILE: import.meta.env.MODE ?? 'dev',
  IS_DEV: import.meta.env.DEV,
  IS_PROD: import.meta.env.PROD,
} as const;
