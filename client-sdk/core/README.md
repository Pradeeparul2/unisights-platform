# 📊 wasm-analytics (Rust WebAssembly SDK)

This project implements a lightweight, privacy-focused WebAssembly analytics SDK written in Rust. It tracks user interactions on the web (like clicks, scrolls, and page views) and securely exports analytics data with optional AES-GCM encryption.

---

## 🚀 Features

- 🔍 Click tracking
- 🖱️ Scroll depth monitoring
- 📄 Page view + entry/exit logging
- ⏱️ Time-on-page tracking
- 📈 Web Vitals support (LCP, CLS, INP, etc.)
- 🔐 AES-256-GCM encrypted payload export
- 🌐 UTM and device info capture
- 📦 WASM target for frontend JS integration

---

## 🧱 Project Structure

```
wasm-analytics/
├── src/
│   └── lib.rs             # Rust source code (Tracker)
├── Cargo.toml             # Rust project config and deps
├── pkg/                   # Output of wasm-pack build
└── README.md              # You are here
```

---

## 🛠 Prerequisites

- [Rust](https://rust-lang.org)
- [wasm-pack](https://rustwasm.github.io/wasm-pack/)

Install wasm-pack:

```bash
cargo install wasm-pack
```

---

## ⚙️ Build Setup

Build the WebAssembly package (for frontend JS usage):

```bash
wasm-pack build --release --target web
```

This generates:

- `pkg/wasm_analytics.js`
- `pkg/wasm_analytics_bg.wasm`

---

## 🔐 Encryption

- Key derivation: PBKDF2-HMAC-SHA256 (100,000 iterations)
- AES-GCM (256-bit key, 96-bit nonce)
- Use `.set_encryption_key(passphrase, salt)` to configure

To export an encrypted payload:

```rust
tracker.export_encrypted_payload()
```

---

## 🧪 Quick Test in JS

```js
import init, { Tracker } from "./pkg/wasm_analytics.js";

await init("./pkg/wasm_analytics_bg.wasm");
const tracker = new Tracker();
tracker.set_session_info("asset", "session", location.href, {}, {});
tracker.log_click(100, 200);
const encrypted = tracker.export_encrypted_payload();
console.log(encrypted);
```

---

## 📉 Optional Optimization

```bash
wasm-strip pkg/wasm_analytics_bg.wasm
wasm-opt -Oz -o pkg/wasm_analytics_bg_opt.wasm pkg/wasm_analytics_bg.wasm
```

---

## 📜 License

Licensed under the [MIT License](https://github.com/<your-username>/unisights/blob/main/LICENSE)—see the root `LICENSE` file for details.

---
