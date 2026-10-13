# DashboardPack Card Validation API

A clean, asynchronous card validation REST API utilizing WooCommerce and Stripe Elements with 3D Secure (3DS2) authentication support. Built with Flask and designed for seamless serverless deployment on **Vercel**.

---

## 🚀 Features

- **WooCommerce + Stripe Elements Integration:** Full flow with dynamic token and nonce extraction.
- **3DS2 Handling:** Automatic fingerprinting authentication and challenge status detection.
- **Anti-Bot & TLS Fingerprint Bypass:** Powered by `curl_cffi` Chrome impersonation.
- **RESTful Endpoints:** Supports both `GET` query parameters and `POST` JSON payloads.
- **Vercel Ready:** Pre-configured `vercel.json` for serverless deployment.
- **CORS Enabled:** Can be integrated with any frontend application or dashboard.

---

## 📁 Project Structure

```
├── index.py              # Unified API application (Flask routes + Gateway logic)
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel deployment configuration
├── .gitignore            # Git ignore file
└── README.md             # Documentation
```

---

## 🛠️ API Reference

### 1. Card Validation

- **URL:**  `/api/stripe1`
- **Methods:** `GET`, `POST`

#### A. GET Request
```http
GET /api/validate?auth=CARD_NUMBER|MM|YY|CVC
```

**Optional Query Parameters:**
- `proxy` - Proxy string in format `ip:port:user:pass`
- `hcaptcha_token` - Radar hCaptcha token (if required)

**Example:**
```bash
curl "http://localhost:5000/api/validate?auth=5195980023444612|04|27|143"
```

---

#### B. POST Request
```http
POST /api/validate
Content-Type: application/json
```

**JSON Payload (Format 1 - Auth String):**
```json
{
  "auth": "5195980023444612|04|27|143",
  "proxy": "ip:port:user:pass"
}
```

**JSON Payload (Format 2 - Structured):**
```json
{
  "card": "5195980023444612",
  "month": "04",
  "year": "27",
  "cvc": "143",
  "proxy": "ip:port:user:pass"
}
```

---

### 2. Response Formats

#### ✅ Success (Card Approved)
```json
{
  "card": "5195980023444612|04|27|143",
  "gateway": "DashboardPack",
  "status": "success",
  "message": "Payment method added successfully",
  "payment_method_id": "pm_1UP...",
  "setup_intent_id": "seti_1UP..."
}
```

#### ⚠️ 3DS Required / Challenge
```json
{
  "card": "5195980023444612|04|27|143",
  "gateway": "DashboardPack",
  "status": "3ds",
  "message": "3DS challenge required",
  "payment_method_id": "pm_1UP...",
  "setup_intent_id": "seti_1UP...",
  "redirect_3ds": "https://hooks.stripe.com/..."
}
```

#### ❌ Declined
```json
{
  "card": "5195980023444612|04|27|143",
  "gateway": "DashboardPack",
  "status": "declined",
  "message": "Your card was declined.",
  "payment_method_id": "pm_1UP...",
  "setup_intent_id": null
}
```

#### ⚠️ Validation Error
```json
{
  "card": "5195980023444612|04|27|143",
  "gateway": "DashboardPack",
  "status": "error",
  "message": "Invalid card number (Failed Luhn validation)"
}
```

---

### 3. Health Check

- **URL:** `/api/health`
- **Method:** `GET`

```json
{
  "gateway": "DashboardPack",
  "status": "healthy"
}
```

---

## 💻 Local Setup & Running

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Server:**
   ```bash
   python index.py
   ```
   The API will be available at `http://localhost:5000`.

---

## ☁️ Deployment on Vercel

### Method 1: Using Vercel CLI
```bash
npm install -g vercel
vercel
```

### Method 2: Git Repository Import
1. Push this folder to a GitHub repository.
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New > Project**.
3. Import the repository.
4. Click **Deploy**. Vercel will automatically detect the Python environment and configure the serverless function.
