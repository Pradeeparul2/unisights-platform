import { Tracker } from "../rust-wasm/pkg/wasm_analytics";
import { v4 as uuidv4 } from "uuid";

interface AnalyticsConfig {
  endpoint: string;
}

export async function initAnalytics(config: AnalyticsConfig): Promise<void> {
  try {
    // Generate anonymized session ID (Privacy-First: no cookies, no fingerprinting)
    let sessionId = sessionStorage.getItem("analytics_session_id");
    if (!sessionId) {
      sessionId = uuidv4();
      sessionStorage.setItem("analytics_session_id", sessionId ?? "");
    } else {
      // Ensure sessionId is a string for later usage
      sessionId = String(sessionId);
    }

    const tracker = new Tracker();
    let startTime = performance.now();

    // Capture clicks with coordinates for heatmap
    window.addEventListener("click", (event) => {
      console.log("Click detected at:", event.clientX, event.clientY);
      tracker.log_click(event.clientX, event.clientY);
    });

    let lastScrollUpdate = -50;
    const scrollIntervalMs = 50;
    window.addEventListener("scroll", () => {
      const now = performance.now();
      if (now - lastScrollUpdate < scrollIntervalMs) return;
      lastScrollUpdate = now;
      const scrollHeight = document.body.scrollHeight || 1;
      const scrollPercent =
        ((window.scrollY + window.innerHeight) / scrollHeight) * 100;
      tracker.update_scroll(scrollPercent);
    });

    setInterval(() => {
      const now = performance.now();
      tracker.tick((now - startTime) / 1000);
      startTime = performance.now();
      const payload = tracker.export_data();
      console.log("Sending payload:", payload);
      if (typeof payload === "object" && payload !== null) {
        const formattedPayload = {
          session_id: sessionId,
          page_url: window.location.href, // For per-page stats
          clicks: payload.clicks.map((click: any) => ({
            x: Number(click.x),
            y: Number(click.y),
            timestamp: click.timestamp,
          })),
          scroll_depth: Number(payload.scroll_depth),
          time_on_page: Number(payload.time_on_page),
        };
        const jsonPayload = JSON.stringify(formattedPayload);
        const blob = new Blob([jsonPayload], { type: "application/json" });
        const success = navigator.sendBeacon(config.endpoint, blob);
        console.log(
          "sendBeacon success:",
          success,
          "Endpoint:",
          config.endpoint
        );
        if (!success) console.warn("Failed to send analytics data");
      } else {
        console.error("Invalid payload:", payload);
      }
    }, 15000);
  } catch (error) {
    console.error("Error initializing analytics:", error);
    throw error;
  }
}
