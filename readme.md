# 💱 Currency Exchange & P2P Wallet Platform — Backend

> **EECE430L Final Project**  
> **Student**: Zein Khamis  
> **Framework**: Flask (Python)  
> **Authentication**: Firebase

---

## 🚀 Project Overview

A complete backend system for a currency exchange and P2P wallet platform built using Flask. It supports real-time exchange rates, secure wallets, peer-to-peer trading, automated exchange triggers, predictive analytics, and optional image-based currency recognition.

---

## 🧠 Key Features

- 🔒 **Secure Firebase Authentication** for user sign-up/login
- 💼 **Multi-currency Wallet System** with deposit functionality
- ♻️ **P2P Exchange** with escrow and rating system
- 📈 **Live Exchange & Gold Rates** via external APIs
- 📊 **Forecasting Module** (Holt-Winters model)
- 🎯 **Auto Exchange Triggers** based on user-defined conditions
- 🌍 **Location-Based Currency Detection** using IP
- 🧠 **(Optional) Currency Recognition** using image classification
- 📦 **Fully tested via Postman** with Swagger UI integration

---

## 📡 API Endpoints (Selected Highlights)

### 🔐 Authentication (Firebase)

- `POST /signUp`
- `POST /signInWithPassword`

### 💰 Wallet

- `POST /api/wallet/deposit` – Deposit funds
- `GET /api/wallet` – Get user wallet

### 🤝 P2P Exchange & Escrow

- `POST /api/orders` – Create a P2P exchange order
- `GET /api/orders` – View all orders
- `POST /api/orders/<order_id>/accept` – Accept order (escrow logic)
- `POST /api/escrow/<escrow_id>/release` – Release escrow funds
- `POST /api/rating` – Submit rating

### 🔁 Auto Exchange Triggers

- `POST /check-triggers` – Set threshold triggers
- `POST /check-live-triggers` – Evaluate trigger conditions

### 📈 Forecast & Historical Rates

- `GET /predict-df` – Forecast currency trends
- `GET /predict-plot` – Forecast plot image
- `GET /historical-df` – Past exchange rates as DataFrame
- `GET /api/historical/<currency>?days=7`

### 🔄 Real-Time Rates

- `GET /api/dashboard-rates`
- `GET /api/live-rates`
- `GET /api/gold-price`
- `GET /api/historical/gold?days=7`

### 🧠 Currency Recognition

- `POST /recognize-currency` – Upload image and classify currency

### 🧾 Transactions

- `POST /transaction` – Add transaction (USD/LBP)
- `GET /transactions` – View all user transactions
- `GET /latest` – Fetch latest transaction

### 🌍 Location-Based Currency Detection

- `GET /detect-currency` – Detect user currency by IP

### 💹 Margin Rate Calculation

- `GET /api/margin/<currency>?percent=x` – Apply profit margin to base exchange rate

---

## 🔐 Security Highlights

- Firebase JWT validation with `@firebase_token_required`
- Role-based authorization for sensitive routes
- SQLAlchemy data constraints (`nullable=False`)
- Input validation for all POST routes
- Rate limiting with `Flask-Limiter` (e.g., `/transaction` = 10 req/min)
- CORS protection using `flask_cors`
- Error handling with custom messages
- Escrow logic to securely hold/release funds in P2P trades

---

## 🧪 Postman Testing

Every route has been validated via Postman. Use the `Authorization` tab with **Bearer Tokens** retrieved from Firebase login. Screenshots and Swagger docs available in the `/docs` folder.

---

## 🛠️ Setup Instructions

1. Clone this repo:

```bash
git clone https://github.com/zein-l/Smart-Municipality-Portal.git
cd Smart-Municipality-Portal

Create and activate a virtual environment:

python -m venv venv
venv\Scripts\activate  # On Windows

Install dependencies:

pip install -r requirements.txt

```

Run the app:

flask run

NOTE : I DID NOT INCLUDE FIREBASE KEY YOU HAVE TO MAKE YOUR OWN 

