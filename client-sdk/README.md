# Insights JavaScript Analytics SDK

This is the JavaScript SDK for the WebAssembly-based analytics tracker built with Rust. It enables lightweight, privacy-respecting user behavior tracking directly in the browser.

## 📦 Features

- Track:
  - Page Views
  - Clicks
  - Scroll Depth
  - Time on Page
  - Web Vitals (CLS, FCP, LCP, INP, TTFB)
  - Custom Events
- UTM parameter capture
- Device and session tracking
- AES-GCM 256-bit encrypted payloads
- Background data flush via `navigator.sendBeacon`

---

## 🚀 Usage

### 1. Include SDK Script in Your HTML

```html
<script
  src="https://yourcdn.com/analytics.js"
  data-insights-id="your-site-id"
  data-analytics-config='{
    "endpoint": "https://your-server.com/analytics",
    "flushIntervalMs": 10000,
    "debug": false
  }'
  defer
></script>

<script
  type="module"
  id="unisights-script"
  defer
  data-insights-id="your-insights-id"
  src="http://localhost:8080/analytics-bundle.min.js"
></script>
```

> The script will automatically initialize once loaded and send periodic batched analytics to the endpoint.

---

## 🛠 Setup Locally

### 1. Install

```bash
pnpm install
```

### 2. Build Rust → WebAssembly

```bash
cd rust-wasm
wasm-pack build --target web
```

The output will be placed in `pkg/`.

### 3. Run Dev

```bash
pnpm run dev
```

Or bundle with Vite/Next.js and deploy the SDK.

---

## 🧠 API Reference

### `window.AnalyticsSDK.init(config?)`

Manually initialize the SDK. Usually auto-loaded by the script.

```ts
await window.AnalyticsSDK.init({
  endpoint: "/analytics",
  flushIntervalMs: 15000,
  debug: true,
});
```

---

### `window.AnalyticsSDK.registerEvent(eventType, handler)`

Attach a custom event listener and log it:

```ts
const logFormSubmit = window.AnalyticsSDK.registerEvent("submit", (e) => {
  return {
    formId: e.target.id,
    timestamp: Date.now(),
  };
});

document.querySelector("#myForm").addEventListener("submit", () => {
  logFormSubmit("form_submit", { status: "sent" });
});
```

---

### `window.AnalyticsSDK.flushNow()`

Immediately send collected events.

```ts
window.AnalyticsSDK.flushNow();
```

---

## 📤 Payload Format (Encrypted)

On every flush, an encrypted payload is sent as:

```json
{
  "ciphertext": "<base64-data>",
  "nonce": "<base64-nonce>"
}
```

Decryption is handled server-side using the AES-GCM key derived from PBKDF2.

---

## 📂 File Structure

```
analytics-sdk/
├── index.html
├── analytics-sdk.ts         # Main JS logic
├── rust-wasm/               # Rust + WASM tracker
│   └── src/lib.rs
├── types.ts                 # Type definitions
├── pkg/                     # wasm-pack output
└── README.md
```

---

## 🔒 Security

- AES-256-GCM encryption of payloads
- PBKDF2-HMAC-SHA256 for key derivation
- Payload sent via `navigator.sendBeacon`

---

## 📃 License

This SDK is private. All rights reserved. Do not redistribute.

---

## 🧑‍💻 Maintainer

Built and maintained by [Your Name / Team].

For help or integration support, contact: [you@example.com]

## 🔐 Example: Before & After Encryption

### 📦 Before Encryption (Raw Analytics Payload)

```json
{
  "asset_id": "abc123",
  "session_id": "session_456",
  "page_url": "https://example.com",
  "events": [
    {
      "type": "Click",
      "data": { "x": 123.4, "y": 567.8, "timestamp": 1625253349000.0 }
    }
  ],
  "scroll_depth": 87.5,
  "time_on_page": 45.0,
  "entry_page": "https://example.com/home",
  "exit_page": "https://example.com/checkout",
  "utm_params": { "utm_source": "google", "utm_medium": "cpc" },
  "device_info": {
    "userAgent": "Mozilla/5.0",
    "platform": "Win32",
    "os": "Windows",
    "screenWidth": 1920,
    "screenHeight": 1080,
    "deviceType": "Desktop"
  }
}
```

### 🔐 After Encryption (Transmitted Payload)

```json
{
  "ciphertext": "QMQihhUeyojicKQ6R2GowipHQQYjAHp0...",
  "nonce": "12mb2A97rcGsMTXk"
}
```

### Docker build comment

```bash
docker build --build-arg INSIGHTS_ENDPOINT=http://127.0.0.1:8000/collect/events --build-arg INSIGHTS_SECRET=insights-secret --build-arg INSIGHTS_SALT=analytics-salt --build-arg INSIGHTS_DEBUG=true -t my-sdk-image .
```
