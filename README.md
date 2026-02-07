# Subscription and Billing Management System Prototype

A lightweight, full-stack prototype for managing subscriptions, plans, and payments. using FastAPI (Backend) and Vanilla HTML/JS (Frontend).

## Features
- **Role-based Auth**: Separate logins for Companies and Users.
- **In-Memory Logic**: No database required, data resets on restart.
- **Plan Management**: Companies can create and view plans.
- **Subscription Flow**: Users can browse plans, subscribe, and pay.
- **Payment Simulation**: Instant payment processing updates subscription status.

## Tech Stack
- **Backend**: Python 3.9+, FastAPI, Uvicorn
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (Fetch API)

## Setup & Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **Access the App**
   Open your browser to: `http://localhost:8000/`

## User Guide

### 1. Test Credentials
- **Company Login**: `admin@techcorp.com` / `password123`
- **User Login**: `alice@example.com` / `password123`

### 2. Company Workflow
1. Login as Company.
2. Create a new "Premium Plan".
3. View list of created plans.
4. Refresh to see new subscribers under "Recent Subscribers".

### 3. User Workflow
1. Login as User.
2. View "Available Plans".
3. Click **Subscribe** on a plan -> Redirects to Checkout.
4. Click **Pay Now** -> Payment Success.
5. Redirects to Dashboard -> Subscription shows as **ACTIVE**.
