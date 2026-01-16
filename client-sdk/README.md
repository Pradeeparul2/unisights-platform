# Unisights Client SDK

Welcome to the **Unisights Client SDK**, the heart of the Unisights real-time analytics platform! This folder contains the WebAssembly (WASM)-powered tracking SDK, built with Rust and TypeScript, designed to efficiently and securely capture user interactions on your website or application. The SDK is lightweight, privacy-focused, and easy to integrate, enabling real-time event tracking with minimal performance impact.

## 🌟 Purpose

The Unisights Client SDK collects events (e.g., page views, clicks, custom actions) directly in the browser using WASM for speed and efficiency. It encrypts data in-browser before sending it to your Unisights ingestion service, ensuring privacy and compliance with regulations like GDPR. This SDK powers the client-side tracking for the Unisights platform, feeding data into Apache Kafka and Druid for real-time analytics.

## 📦 Folder Structure

```
client-sdk/
├── core/                 # Rust WASM core logic (compiled to analytics-bundle.min.js)
├── src/                  # TypeScript wrapper and utilities
├── package.json          # Node.js configuration for building
├── tsconfig.json         # TypeScript configuration
└── README.md             # You are here
```

- **`core/`**: Contains the Rust source code compiled to WASM, providing the high-performance event collection logic.
- **`src/`**: Includes TypeScript files that wrap the WASM module and expose a simple JavaScript API for developers.

## 🚀 Getting Started

### 1️⃣ Prerequisites

- **Node.js** (>= 16.x) with npm
- **Rust** (for building or modifying the WASM core)
- **WasmPack** (install with `cargo install wasm-pack` for development)

### 2️⃣ Install Dependencies

Navigate to the `client-sdk` folder and install dependencies:

```bash
npm install
```

### 3️⃣ Build the SDK

Compile the Rust WASM code and bundle it with TypeScript:

```bash
npm run build
```

This generates `analytics-bundle.min.js` in the `dist/` folder (or configure the output path as needed), ready for deployment.

### 4️⃣ Integrate into Your HTML

Inject the SDK into your website by adding the following `<script>` tag to your HTML file. Replace `your-insights-id` with your unique Unisights API key and adjust the `src` URL to point to your hosted SDK file (e.g., a CDN or local server):

```html
<script
  type="module"
  id="unisights-script"
  defer
  data-insights-id="your-insights-id"
  data-secret="..."
  data-salt="..."
  src="http://localhost:9005/analytics-bundle.min.js"
></script>
```

- **`type="module"`**: Ensures the SDK loads as an ES module.
- **`id="unisights-script"`**: A unique identifier for the script tag.
- **`defer`**: Loads the script asynchronously without blocking HTML parsing.
- **`data-insights-id`**: Your Unisights API key for identifying the data source.
- **`src`**: Path to the compiled `analytics-bundle.min.js` file.

### 5️⃣ Usage

Once loaded, the SDK is available globally as `unisights`. You can track events like this:

```html
<script>
  // Initialize the SDK (optional, auto-runs with data-insights-id)
  unisights.init({ apiKey: "your-insights-id" });

  // Track a custom event
  unisights.track("page_view", {
    path: window.location.pathname,
    timestamp: new Date().toISOString(),
  });

  // Track a click event
  document.querySelector("button").addEventListener("click", () => {
    unisights.track("button_click", { element: "submit-btn" });
  });
</script>
```

- **`init()`**: Configures the SDK with your API key (optional if set in `data-insights-id`).
- **`track(eventName, data)`**: Sends an event with a name and optional metadata to the Unisights ingestion service.

## 🛠 Development

### Modify the WASM Core

- Edit Rust files in `core/`.
- Rebuild with `npm run build` to regenerate `analytics-bundle.min.js`.

### Test Locally

- Serve the `dist/` folder with a local server (e.g., `npx serve dist` or use `http://localhost:9005`).
- Open your HTML file in a browser and check the console for errors or use network tools to verify event transmission.

## ✨ Why This SDK Stands Out

- **WASM Performance**: Rust-compiled WASM offers faster execution and lower overhead than traditional JavaScript trackers.
- **Privacy-Focused**: In-browser encryption protects user data before it leaves the client.
- **Lightweight**: Minimal impact on page load times, ideal for high-traffic sites.
- **Extensible**: Easy to add custom events or integrate with your analytics workflow.

## 🌟 Support the Project

If you find the Unisights Client SDK useful, give the main Unisights repository a ⭐ on GitHub at [https://github.com/<your-username>/unisights](https://github.com/<your-username>/unisights). Share it with your network or suggest improvements via GitHub Issues. More contributors will help us enhance this SDK!

## 📜 License

Licensed under the [MIT License](https://github.com/<your-username>/unisights/blob/main/LICENSE)—see the root `LICENSE` file for details.
