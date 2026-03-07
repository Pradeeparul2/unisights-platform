use wasm_bindgen::prelude::*;
use js_sys::Date;
use serde::{Serialize};
use aes_gcm::{Aes256Gcm, Key, Nonce, aead::{Aead, KeyInit}};
use pbkdf2::pbkdf2_hmac;
use sha2::Sha256;
use base64::{engine::general_purpose, Engine as _};
use serde_json::json;
use serde_wasm_bindgen;
use rand::RngCore;
use rand::rngs::OsRng;
use generic_array::GenericArray;

// Derive AES key using PBKDF2-HMAC-SHA256
fn derive_key(passphrase: &str, salt: &[u8]) -> [u8; 32] {
    let mut key = [0u8; 32];
    pbkdf2_hmac::<Sha256>(
        passphrase.as_bytes(),
        salt,
        100_000,
        &mut key,
    );
    key
}

#[wasm_bindgen]
#[derive(Clone)]
pub struct Tracker {
    events: Vec<Event>,
    scroll_depth: f64,
    time_on_page: f64,
    entry_page: Option<String>,
    exit_page: Option<String>,
    encryption_key: Option<[u8; 32]>,
    encrypt: bool,
    asset_id: Option<String>,
    session_id: Option<String>,
    page_url: Option<String>,
    utm_params: JsValue,
    device_info: JsValue,
}

#[derive(Serialize, Clone)]
#[serde(tag = "type", content = "data")]
enum Event {
    Click { x: f64, y: f64, timestamp: f64 },
    PageView { url: String, timestamp: f64 },
    WebVital {
        name: String,
        value: f64,
        id: String,
        rating: String,
        delta: f64,
        entries: usize,
        navigation_type: String,
        timestamp: f64,
    },
    Custom { name: String, data: String, timestamp: f64 },
}

#[derive(Serialize)]
struct FullAnalyticsPayload {
    asset_id: String,
    session_id: String,
    page_url: String,
    events: Vec<Event>,
    scroll_depth: f64,
    time_on_page: f64,
    entry_page: Option<String>,
    exit_page: Option<String>,
    utm_params: serde_json::Value,
    device_info: serde_json::Value,
}

#[wasm_bindgen]
impl Tracker {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Tracker {
        Tracker {
            events: vec![],
            scroll_depth: 0.0,
            time_on_page: 0.0,
            entry_page: None,
            exit_page: None,
            encryption_key: None,
            encrypt: false,
            asset_id: None,
            session_id: None,
            page_url: None,
            utm_params: JsValue::UNDEFINED,
            device_info: JsValue::UNDEFINED,
        }
    }

    #[wasm_bindgen(js_name = logClick)]
    pub fn log_click(&mut self, x: f64, y: f64) {
        self.events.push(Event::Click {
            x,
            y,
            timestamp: Date::now(),
        });
    }

    #[wasm_bindgen(js_name = logPageView)]
    pub fn log_page_view(&mut self, url: String) {
        self.events.push(Event::PageView {
            url,
            timestamp: Date::now(),
        });
    }

    #[wasm_bindgen(js_name = logEntryPage)]
    pub fn log_entry_page(&mut self, url: String) {
        self.entry_page = Some(url);
    }

    #[wasm_bindgen(js_name = logExitPage)]
    pub fn log_exit_page(&mut self, url: String) {
        self.exit_page = Some(url);
    }

    #[wasm_bindgen(js_name = logCustomEvent)]
    pub fn log_custom_event(&mut self, name: String, data: String) {
        self.events.push(Event::Custom {
            name,
            data,
            timestamp: Date::now(),
        });
    }

    #[wasm_bindgen(js_name = logWebVital)]
    pub fn log_web_vital(
        &mut self,
        name: String,
        value: f64,
        id: String,
        rating: String,
        delta: f64,
        entries: usize,
        navigation_type: String,
    ) {
        self.events.push(Event::WebVital {
            name,
            value,
            id,
            rating,
            delta,
            entries,
            navigation_type,
            timestamp: Date::now(),
        });
    }

    #[wasm_bindgen(js_name = updateScroll)]
    pub fn update_scroll(&mut self, percent: f64) {
        self.scroll_depth = self.scroll_depth.max(percent);
    }

    #[wasm_bindgen(js_name = tick)]
    pub fn tick(&mut self, seconds: f64) {
        self.time_on_page += seconds;
    }

    #[wasm_bindgen(js_name = clearEvents)]
    pub fn clear_events(&mut self) {
        self.events.clear();
    }

    #[wasm_bindgen(js_name = setEncryptionKey)]
    pub fn set_encryption_key(&mut self, passphrase: String, salt: String, encrypt: bool) {
        if !encrypt {
            self.encryption_key = None;
            self.encrypt = false;
            return;
        }
        let key = derive_key(&passphrase, salt.as_bytes());
        self.encryption_key = Some(key);
        self.encrypt = true;
    }

    #[wasm_bindgen(js_name = setSessionInfo)]
    pub fn set_session_info(
        &mut self,
        asset_id: String,
        session_id: String,
        page_url: String,
        utm_params: JsValue,
        device_info: JsValue,
    ) {
        self.asset_id = Some(asset_id);
        self.session_id = Some(session_id);
        self.page_url = Some(page_url);
        self.utm_params = utm_params;
        self.device_info = device_info;
    }

    // New method to update page_url
    #[wasm_bindgen(js_name = setPageUrl)]
    pub fn set_page_url(&mut self, page_url: String) {
        self.page_url = Some(page_url);
    }

    #[wasm_bindgen(js_name = exportEncryptedPayload)]
    pub fn export_encrypted_payload(&self) -> Result<JsValue, JsValue> {
        if self.events.is_empty() {
            return Err(JsValue::from_str("No events to export"));
        }

        let payload = FullAnalyticsPayload {
            asset_id: self.asset_id.clone().ok_or("Missing asset_id")?,
            session_id: self.session_id.clone().ok_or("Missing session_id")?,
            page_url: self.page_url.clone().ok_or("Missing page_url")?,
            events: self.events.clone(),
            scroll_depth: self.scroll_depth,
            time_on_page: self.time_on_page,
            entry_page: self.entry_page.clone(),
            exit_page: self.exit_page.clone(),
            utm_params: serde_wasm_bindgen::from_value(self.utm_params.clone())
                .map_err(|e| JsValue::from_str(&format!("UTM decode error: {}", e)))?,
            device_info: serde_wasm_bindgen::from_value(self.device_info.clone())
                .map_err(|e| JsValue::from_str(&format!("Device decode error: {}", e)))?,
        };

        let json = serde_json::to_vec(&payload)
            .map_err(|e| JsValue::from_str(&format!("Serialization error: {}", e)))?;

        if !self.encrypt {
            let out = json!({
                "data": serde_json::from_slice::<serde_json::Value>(&json).unwrap(),
                "encrypted": false,
            });
            return serde_wasm_bindgen::to_value(&out)
                .map_err(|e| JsValue::from_str(&format!("Conversion error: {}", e)));
        }

        // Encrypted payload
        let key = self
            .encryption_key
            .ok_or_else(|| JsValue::from_str("Encryption key not set"))?;

        let (ciphertext, nonce) = encrypt_data(&json, &key)?;

        let out = json!({
            "data": general_purpose::STANDARD.encode(ciphertext),
            "id": general_purpose::STANDARD.encode(nonce),
            "encrypted": true,
        });

        serde_wasm_bindgen::to_value(&out)
            .map_err(|e| JsValue::from_str(&format!("Conversion error: {}", e)))
    }
}

fn encrypt_data(plain: &[u8], key_bytes: &[u8; 32]) -> Result<(Vec<u8>, Vec<u8>), JsValue> {
    let cipher = Aes256Gcm::new(aes_gcm::Key::<Aes256Gcm>::from_slice(key_bytes));

    let mut nonce = [0u8; 12];
    OsRng.fill_bytes(&mut nonce);
    let nonce_arr = GenericArray::from_slice(&nonce);

    let encrypted = cipher
        .encrypt(nonce_arr, plain)
        .map_err(|e| JsValue::from_str(&format!("Encryption error: {:?}", e)))?;

    Ok((encrypted, nonce.to_vec()))
}