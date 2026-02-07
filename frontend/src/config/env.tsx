export const ENV = {
  PROFILE: import.meta.env.MODE ?? 'dev',
  IS_DEV: (import.meta.env.MODE ?? 'dev') === 'dev',
  IS_OP: (import.meta.env.MODE ?? 'dev') === 'op',
} as const;
