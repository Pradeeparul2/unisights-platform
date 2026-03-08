# Unisights Client SDK

The Unisights analytics is a WebAssembly-powered analytics tracker built with Rust and TypeScript. It captures user interactions in the browser, encrypts data client-side, and sends it securely to your Unisights ingestion service — with minimal performance impact.

---

## ✨ Why Unisights

- **WASM Performance** — Rust-compiled WASM offers faster execution and lower overhead than traditional JS trackers
- **Client-Side Encryption** — Data is encrypted in the browser before it ever leaves the client
- **Lightweight** — ~86KB gzipped, including WASM binary and web vitals tracking
- **Web Vitals Built-in** — Automatically tracks CLS, INP, LCP, FCP, and TTFB
- **SPA Ready** — Handles `pushState`, `replaceState`, and `popstate` for React, Next.js, Vue, etc.

---

## 📦 Installation

```bash
npm install @unisights/analytics
# or
pnpm add @unisights/analytics
# or
yarn add @unisights/analytics
```

---

## 🚀 Usage

### Option 1 — CDN / Script Tag (Recommended)

Add the script tag to your HTML `<head>`. The SDK auto-initializes and exposes `window.unisights`.

```html
<script
  type="module"
  id="unisights-script"
  async
  data-insights-id="your-insights-id"
  data-secret="your-secret"
  data-salt="your-salt"
  src="https://cdn.jsdelivr.net/npm/@unisights/analytics@X.X.X/dist/unisights.min.js"
></script>
```

Then use it anywhere in your app:

```javascript
// Wait for SDK to be ready
window.unisights?.init();

// Log a custom event
window.unisights?.log("signup", { plan: "pro" });

// Flush events immediately
window.unisights?.flushNow();

// Register a custom event handler
const track = window.unisights?.registerEvent("click", (e) => {});
track("button_click", { id: "submit-btn" });
```

#### Usage in React / Next.js

```tsx
import { useEffect } from "react";

export default function Layout({ children }) {
  useEffect(() => {
    const script = document.getElementById(
      "unisights-script",
    ) as HTMLScriptElement;

    const initSDK = () => {
      window.unisights?.init().catch(console.error);
    };

    if (window.unisights) {
      initSDK();
    } else {
      script?.addEventListener("load", initSDK);
      return () => script?.removeEventListener("load", initSDK);
    }
  }, []);

  return <>{children}</>;
}
```

---

### Option 2 — Manual Init (Script Tag)

If you prefer to control when the SDK initializes, omit `data-insights-id` and call `init()` manually:

```html
<script
  type="module"
  id="unisights-script"
  async
  data-insights-id="your-insights-id"
  data-secret="your-secret"
  data-salt="your-salt"
  src="https://cdn.jsdelivr.net/npm/@unisights/analytics@X.X.X/dist/unisights.min.js"
></script>

<script type="module">
  await window.unisights.init({
    endpoint: "https://your-ingestion-endpoint.com/collect",
    debug: true,
  });
</script>
```

---

## ⚙️ Configuration

All options are passed to `init()` or via `data-analytics-config` on the script tag.

| Option            | Type      | Default         | Description                     |
| ----------------- | --------- | --------------- | ------------------------------- |
| `endpoint`        | `string`  | env var         | URL to send analytics events to |
| `insightsId`      | `string`  | from script tag | Your Unisights project ID       |
| `debug`           | `boolean` | `false`         | Log events to the console       |
| `flushIntervalMs` | `number`  | `15000`         | How often to flush events (ms)  |
| `trackPageViews`  | `boolean` | `true`          | Auto-track page views           |
| `trackClicks`     | `boolean` | `true`          | Auto-track click events         |
| `trackScroll`     | `boolean` | `true`          | Auto-track scroll depth         |

---

## 🧩 API Reference

### `window.unisights.init(config?)`

Initializes the SDK. Must be called before using other methods if auto-init is disabled.

```javascript
await window.unisights.init({
  endpoint: "https://your-endpoint.com/collect",
  debug: true,
});
```

### `window.unisights.log(name, data)`

Log a custom event with optional metadata.

```javascript
window.unisights.log("purchase", {
  item: "pro-plan",
  amount: 49.99,
  currency: "USD",
});
```

### `window.unisights.flushNow()`

Immediately send all buffered events to the endpoint.

```javascript
window.unisights.flushNow();
```

### `window.unisights.registerEvent(eventType, handler)`

Register a DOM event listener and get back a function to log custom events.

```javascript
const track = window.unisights.registerEvent("click", (e) => {
  console.log("click captured", e);
});

// Later, log an event tied to this listener
track("cta_click", { label: "Get Started" });
```

---

## 🏗 TypeScript Support

The package ships with type declarations. If you use the SDK via script tag and want `window.unisights` typed in your TypeScript project, install the package for types only:

```bash
npm install @unisights/analytics
```

TypeScript will automatically pick up the `Window` augmentation — no extra configuration needed.

```typescript
// Fully typed — no @ts-ignore needed
window.unisights?.log("event", { data: "value" });
```

---

## 📜 License

MIT — see [LICENSE](./LICENSE) for details.
