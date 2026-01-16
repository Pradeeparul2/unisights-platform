// analytics-sdk.ts
import initWasm, * as wasm from "../core/pkg/unisights_core.js";
import type { AnalyticsConfig, EventHandler, DeviceData } from "./types";
import {
  onCLS,
  onINP,
  onLCP,
  onFCP,
  onTTFB,
  Metric as WebVital,
} from "web-vitals";

interface AnalyticsSDK {
  init: (config: Partial<AnalyticsConfig>) => Promise<void>;
  registerEvent: (
    eventType: string,
    handler: EventHandler
  ) => (name: string, data: any) => void;
  flushNow: () => void;
  log: (name: string, data: any) => void;
}

declare global {
  interface Window {
    AnalyticsSDK?: AnalyticsSDK;
    AnalyticsQueue?: Array<() => void>;
  }
}

declare const process: {
  env: {
    INSIGHTS_SECRET: string;
    INSIGHTS_SALT: string;
    INSIGHTS_ENDPOINT?: string;
    INSIGHTS_DEBUG?: string;
  };
};

// Dynamically determine the base URL of the script
const getScriptBaseUrl = () => {
  const script = document.getElementById(
    "unisights-script"
  ) as HTMLScriptElement | null;
  const scriptSrc = script?.src || "";
  const baseUrl = scriptSrc.substring(0, scriptSrc.lastIndexOf("/")) || "";
  return baseUrl;
};

const defaultConfig: AnalyticsConfig = {
  endpoint: process.env.INSIGHTS_ENDPOINT || "",
  debug: process.env.INSIGHTS_DEBUG === "true",
  flushIntervalMs: 15000, // 15 seconds
  wasmPath: `${getScriptBaseUrl()}/pkg/unisights_core_bg.wasm`,
  trackPageViews: true,
  trackClicks: true,
  trackScroll: true,
};

function reportWebVitals(tracker: wasm.Tracker, config: AnalyticsConfig) {
  const report = (metric: WebVital) => {
    try {
      tracker.logWebVital(
        metric.name,
        metric.value,
        metric.id,
        metric.rating,
        metric.delta,
        metric.entries?.length || 0,
        metric.navigationType || "navigate"
      );
      config.debug && console.log("[Insights] - Web Vital logged:", metric);
    } catch (e) {
      console.error("[Insights] - Web Vital Error:", e);
    }
  };
  [onCLS, onINP, onLCP, onFCP, onTTFB].forEach((fn) => fn(report));
}

function getUTMParams(): Record<string, string> {
  const keys = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
  ];
  const params: Record<string, string> = {};
  const url = new URLSearchParams(window.location.search);
  for (const key of keys) {
    const value = url.get(key) || sessionStorage.getItem(`_us_${key}`);
    if (value) {
      params[key] = value;
      sessionStorage.setItem(`_us_${key}`, value);
    }
  }
  return params;
}

function getDeviceInfo(): DeviceData {
  const ua = navigator.userAgent;
  const platform = navigator.platform;
  const os = /Win/.test(platform)
    ? "Windows"
    : /Mac/.test(platform)
    ? "macOS"
    : /Linux/.test(platform)
    ? "Linux"
    : /Android/.test(ua)
    ? "Android"
    : /iPhone|iPad|iPod/.test(ua)
    ? "iOS"
    : "Unknown";

  const deviceType = /Mobi|Android/i.test(ua) ? "Mobile" : "Desktop";
  return {
    userAgent: ua,
    platform,
    os,
    screenWidth: screen.width,
    screenHeight: screen.height,
    deviceType,
  };
}

const isBot = /bot|crawler|spider|crawling/i.test(navigator.userAgent);

const SESSION_KEY = "__ua_session";
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 min

function getOrCreateSession(): string {
  const now = Date.now();
  const stored = localStorage.getItem(SESSION_KEY);

  if (stored) {
    const session = JSON.parse(stored);

    // still active?
    if (now - session.lastActivity < SESSION_TIMEOUT) {
      session.lastActivity = now;
      localStorage.setItem(SESSION_KEY, JSON.stringify(session));
      return session.sessionId;
    }
  }

  // create new session
  const session = {
    sessionId: crypto.randomUUID(),
    startedAt: now,
    lastActivity: now,
  };

  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session.sessionId;
}

function touchSession() {
  const stored = localStorage.getItem(SESSION_KEY);
  if (!stored) return;

  const session = JSON.parse(stored);
  session.lastActivity = Date.now();
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

let isInitialized = false;
let flushTimer: number | undefined = undefined;
let currentPageUrl = location.href; // Track current page URL

async function initAnalytics(
  userConfig: Partial<AnalyticsConfig> = {}
): Promise<void> {
  if (isInitialized) return;
  isInitialized = true;

  const tag = document.querySelector("script[data-insights-id]");
  const id = tag?.getAttribute("data-insights-id");
  const secret = tag?.getAttribute("data-secret")!;
  const salt = tag?.getAttribute("data-salt")!;
  if (!id) throw new Error("Missing data-insights-id");

  let tagConfig: Partial<AnalyticsConfig> = {};
  try {
    tagConfig = JSON.parse(tag?.getAttribute("data-analytics-config") || "{}");
  } catch (e) {
    console.error("[Insights] - Config parse error:", e);
  }

  if (isBot) return;

  const config = {
    ...defaultConfig,
    ...tagConfig,
    ...userConfig,
    insightsId: id,
  };

  await initWasm(config.wasmPath);
  const tracker = new wasm.Tracker();
  const sessionId = getOrCreateSession();
  let start = performance.now();
  let pending = false;

  tracker.setEncryptionKey(
    secret || process.env.INSIGHTS_SECRET,
    salt || process.env.INSIGHTS_SALT
  );
  tracker.setSessionInfo(
    config.insightsId,
    sessionId,
    location.href,
    getUTMParams(),
    getDeviceInfo()
  );

  reportWebVitals(tracker, config);
  config.debug && console.log("[Insights] - Session ID:", sessionId);

  const eventMap = new Map<string, EventListener>();

  if (config.trackClicks) {
    const clickHandler = (e: MouseEvent) => {
      tracker.logClick(e.clientX, e.clientY);
      touchSession();
      pending = true;
    };
    window.addEventListener("click", clickHandler);
    eventMap.set("click", clickHandler as EventListener);
  }

  if (config.trackScroll) {
    let last = -50;
    const scrollHandler = () => {
      const now = performance.now();
      if (now - last < 50) return;
      last = now;
      const percent =
        ((window.scrollY + window.innerHeight) /
          (document.body.scrollHeight || 1)) *
        100;
      tracker.updateScroll(percent);
      touchSession();
      pending = true;
    };
    window.addEventListener("scroll", scrollHandler);
    eventMap.set("scroll", scrollHandler);
  }

  if (config.trackPageViews) {
    tracker.logEntryPage(location.href);
    tracker.logPageView(location.href);
    if (config.debug)
      console.log("[Insights] - Entry page event:", location.href);
    pending = true;
  }

  // Handle SPA navigation
  const handleNavigation = () => {
    const newUrl = location.href;
    if (newUrl !== currentPageUrl) {
      // Flush pending events for the current page
      if (pending) {
        sendAnalytics(tracker, config);
        pending = false;
      }
      // Update page URL
      currentPageUrl = newUrl;
      // Assuming wasm.Tracker has a method to update page URL, e.g., setPageUrl
      // If not, you may need to extend the WASM module or reset session info
      // SPA navigation: avoid resetting full session info
      // tracker.setSessionInfo(
      //   config.insightsId,
      //   sessionId,
      //   currentPageUrl,
      //   getUTMParams(),
      //   getDeviceInfo()
      // );
      // Log new page view
      if (config.trackPageViews) {
        tracker.logPageView(currentPageUrl);
        if (config.debug)
          console.log("[Insights] - Page view event:", currentPageUrl);
        touchSession();
        pending = true;
      }
    }
  };

  // Listen for SPA navigation events
  window.addEventListener("popstate", handleNavigation);
  // Optionally, use history.pushState/replaceState override for SPAs
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;
  history.pushState = function (...args) {
    originalPushState.apply(this, args);
    handleNavigation();
  };
  history.replaceState = function (...args) {
    originalReplaceState.apply(this, args);
    handleNavigation();
  };

  const pagehideHandler = () => {
    tracker.logExitPage(currentPageUrl);
    if (config.debug)
      console.log(
        "[Insights] - Exit page (via pagehide) event:",
        currentPageUrl
      );
    sendAnalytics(tracker, config, true);
    touchSession();
    pending = false;
  };
  window.addEventListener("pagehide", pagehideHandler);

  // Use visibilitychange to flush before backgrounding
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      sendAnalytics(tracker, config, true);
      pending = false;
    }
  });

  flushTimer = window.setInterval(() => {
    const now = performance.now();
    tracker.tick((now - start) / 1000);
    start = now;
    if (pending) {
      sendAnalytics(tracker, config);
      pending = false;
    }
  }, config.flushIntervalMs);

  window.AnalyticsSDK = {
    init: initAnalytics,
    registerEvent: (eventType, handler) => {
      const bound = typeof handler === "function" ? handler : () => {};
      window.addEventListener(eventType, bound);
      eventMap.set(eventType, bound);
      return (name: string, data: any) => {
        try {
          tracker.logCustomEvent(name, JSON.stringify(data));
          pending = true;
        } catch (e) {
          console.error("[Insights] - Custom Event Error:", e);
        }
      };
    },
    flushNow: () => sendAnalytics(tracker, config, true),
    log: (name: string, data: any) => {
      try {
        tracker.logCustomEvent(name, JSON.stringify(data));
        touchSession();
        pending = true;
      } catch (e) {
        console.error("[Insights] - log() error:", e);
      }
    },
  };

  if (Array.isArray(window.AnalyticsQueue)) {
    window.AnalyticsQueue.splice(0).forEach((fn) => {
      try {
        fn();
      } catch (e) {
        console.error("[Insights] - Queue Error:", e);
      }
    });
  }
}

function sendAnalytics(
  tracker: wasm.Tracker,
  config: AnalyticsConfig,
  final: boolean = false
): void {
  try {
    const encrypted = tracker.exportEncryptedPayload();
    if (config.debug) console.log("[Insights] - Payload:", encrypted);
    if (!encrypted || encrypted instanceof Error) return;

    // Convert JsValue (from wasm) into plain JS object
    const encryptedObj =
      encrypted instanceof Map
        ? Object.fromEntries(encrypted.entries())
        : encrypted;

    const blob = new Blob([JSON.stringify(encryptedObj)], {
      type: "application/json",
    });

    const sent = navigator.sendBeacon(config.endpoint, blob);

    config.debug &&
      console.log("[Insights] - Encrypted payload sent:", {
        success: sent,
        length: blob.size,
      });

    if (sent) tracker.clearEvents();
  } catch (err) {
    console.error("[Insights] - Send Error:", err);
  }
}

if (typeof window !== "undefined") {
  window.AnalyticsQueue ||= [];
  initAnalytics().catch((e) => console.error("[Insights] - Init Error:", e));
}
