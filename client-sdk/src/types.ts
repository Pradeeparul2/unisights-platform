export interface AnalyticsConfig {
  endpoint: string;
  insightsId?: string;
  debug?: boolean;
  flushIntervalMs?: number;
  wasmPath?: string;
  trackPageViews?: boolean;
  trackClicks?: boolean;
  trackScroll?: boolean;
}

export interface DeviceData {
  userAgent: string;
  platform: string;
  os: string;
  screenWidth: number;
  screenHeight: number;
  deviceType: string;
}

export type EventHandler =
  | ((event: Event) => void)
  | (() => (event: Event) => void);

export type AnalyticsSDK = {
  init: (config: Partial<AnalyticsConfig>) => Promise<void>;
  registerEvent: (eventType: string, handler: EventHandler) => void;
};
