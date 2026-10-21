from flask import Flask, request, jsonify, render_template_string
import os
import requests
import base64
from datetime import datetime, timezone
import json

app = Flask(__name__)

# ===== CONFIG — Loaded from Render Environment =====
MPESA_CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.environ.get("MPESA_SHORTCODE")
MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY")
MPESA_ENVIRONMENT = os.environ.get("MPESA_ENVIRONMENT", "sandbox")
BASE_URL = os.environ.get("BASE_URL", "https://aurem-v11-prod.onrender.com")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("JARVIS_SUPABASE_CONTROL_TOKEN")
WA_ACCESS_TOKEN = os.environ.get("WA_ACCESS_TOKEN", "")
WA_PHONE_NUMBER_ID = os.environ.get("WA_PHONE_NUMBER_ID", "")

MPESA_API = "https://sandbox.safaricom.co.ke" if MPESA_ENVIRONMENT == "sandbox" else "https://api.safaricom.co.ke"

# ===== HELPER: Get OAuth Token =====
def get_mpesa_token():
    url = f"{MPESA_API}/oauth/v1/generate?grant_type=client_credentials"
    auth = base64.b64encode(f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    resp = requests.get(url, headers=headers, timeout=30)
    return resp.json()["access_token"]

# ===== HELPER: Save to Supabase =====
def log_to_supabase(table: str, data: dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print(f"[SUPABASE_SKIP] {table}: {json.dumps(data)}")
        return
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers, json=data, timeout=30)

# ===== HELPER: Send WhatsApp Alert =====
def send_whatsapp(recipient: str, message: str):
    if not WA_ACCESS_TOKEN or not WA_PHONE_NUMBER_ID:
        print(f"[WA_SKIP] → {recipient}: {message[:60]}...")
        return
    url = f"https://graph.facebook.com/v19.0/{WA_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WA_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=payload, timeout=30)

# ===== 1. INITIATE STK PUSH =====
@app.route("/api/mpesa/pay", methods=["POST"])
def initiate_payment():
    data = request.get_json()
    phone = data.get("phone", "").strip()
    amount = int(data.get("amount", 2500))
    plan = data.get("plan", "starter")

    if not phone.startswith("254"):
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("7"):
            phone = "254" + phone

    token = get_mpesa_token()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()

    callback_url = f"{BASE_URL}/api/mpesa/callback"
    stk_payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": f"JARVIS-{plan.upper()}",
        "TransactionDesc": f"JARVIS {plan} subscription"
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(f"{MPESA_API}/mpesa/stkpush/v1/processrequest", headers=headers, json=stk_payload, timeout=30)
    result = resp.json()

    log_to_supabase("payment_intents", {
        "phone": phone,
        "amount": amount,
        "plan": plan,
        "checkout_request_id": result.get("CheckoutRequestID"),
        "merchant_request_id": result.get("MerchantRequestID"),
        "status": "PENDING",
        "environment": MPESA_ENVIRONMENT
    })

    return jsonify({
        "status": "PENDING",
        "message": "STK Push sent — check your phone",
        "checkout_id": result.get("CheckoutRequestID"),
        "phone": phone,
        "amount": amount
    })

# ===== 2. CALLBACK — M-Pesa Confirms Payment =====
@app.route("/api/mpesa/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json()
    body = data.get("Body", {})
    stk = body.get("stkCallback", {})
    result_code = stk.get("ResultCode")
    checkout_id = stk.get("CheckoutRequestID", "UNKNOWN")

    if result_code == 0:
        meta = {item["Name"]: item["Value"] for item in stk.get("CallbackMetadata", {}).get("Item", [])}
        amount = meta.get("Amount")
        receipt = meta.get("MpesaReceiptNumber")
        phone = meta.get("PhoneNumber")

        log_to_supabase("confirmed_payments", {
            "checkout_request_id": checkout_id,
            "amount": amount,
            "receipt_number": receipt,
            "phone": phone,
            "status": "SUCCESS",
            "confirmed_at": datetime.now(timezone.utc).isoformat()
        })

        send_whatsapp(phone, f"""✅ PAYMENT CONFIRMED — JARVIS ECOSYSTEM

Amount: KES {amount:,}
Receipt: {receipt}
Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}

Welcome to the JARVIS ecosystem! Your access is now active.
""")

        print(f"✅ PAID — {phone} → KES {amount} — {receipt}")
    else:
        log_to_supabase("failed_payments", {
            "checkout_request_id": checkout_id,
            "result_code": result_code,
            "result_desc": stk.get("ResultDesc"),
            "status": "FAILED"
        })
        print(f"❌ FAILED — {checkout_id} → Code {result_code}")

    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

# ===== 3. STATUS CHECK =====
@app.route("/api/mpesa/status/<checkout_id>", methods=["GET"])
def check_status(checkout_id):
    return jsonify({"checkout_id": checkout_id, "status": "pending"})

# ===== 4. HEALTH =====
@app.route("/health")
def health():
    return jsonify({
        "build": "V21-MPESA-ENGINE",
        "status": "OPERATIONAL",
        "environment": MPESA_ENVIRONMENT,
        "mpesa_connected": bool(MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET),
        "supabase_connected": bool(SUPABASE_URL and SUPABASE_KEY),
        "whatsapp_enabled": bool(WA_ACCESS_TOKEN and WA_PHONE_NUMBER_ID)
    })

# ===== 5. PAYMENT PAGE =====
@app.route("/pay")
def pay_page():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>JARVIS — Activate Access</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{background:#0a0a0f;color:#fff;font-family:system-ui;padding:2rem;max-width:500px;margin:0 auto}
        .card{background:#12121f;border-radius:16px;padding:2rem;margin:1rem 0}
        h1{color:#4ade80}
        .plan{border:2px solid #222;border-radius:12px;padding:1rem;margin:0.5rem 0;cursor:pointer}
        .plan.selected{border-color:#4ade80;background:#0f1f15}
        input{width:100%;padding:0.8rem;margin:0.5rem 0;border-radius:8px;border:none;background:#1e1e2f;color:#fff}
        button{width:100%;padding:1rem;background:#4ade80;color:#000;font-weight:bold;border:none;border-radius:8px;font-size:1rem;cursor:pointer;margin-top:1rem}
        button:disabled{opacity:0.5;cursor:not-allowed}
        .status{margin-top:1rem;padding:1rem;border-radius:8px;display:none}
        .loading{background:#1a2a3a;display:block}
        .success{background:#0f2a1a;display:block;color:#4ade80}
        .error{background:#2a0f0f;display:block;color:#f87171}
    </style>
</head>
<body>
    <h1>⚡ JARVIS Access</h1>
    <p>Select your plan → enter your phone → approve on your device</p>

    <div class="card">
        <label class="plan selected" data-amount="2500" data-plan="starter">
            <input type="radio" name="plan" checked style="display:none">
            <strong>STARTER</strong><br>
            KES 2,500 — Full V21 Access
        </label>
        <label class="plan" data-amount="7500" data-plan="pro">
            <input type="radio" name="plan" style="display:none">
            <strong>PRO</strong><br>
            KES 7,500 — +Orchestrator + Recurring Revenue
        </label>
        <label class="plan" data-amount="25000" data-plan="founder">
            <input type="radio" name="plan" style="display:none">
            <strong>FOUNDER</strong><br>
            KES 25,000 — Priority + Custom Domains + 20% Commissions
        </label>

        <input type="tel" id="phone" placeholder="Your phone e.g. 0712345678" maxlength="10">
        <button id="payBtn">Send Payment Prompt</button>

        <div id="statusLoading" class="status loading">
            ⏳ Sending prompt to your phone...<br>
            Please check your M-Pesa popup.
        </div>
        <div id="statusSuccess" class="status success">
            ✅ Payment confirmed! Access activated.<br>
            Check WhatsApp for your receipt.
        </div>
        <div id="statusError" class="status error">
            ❌ Something went wrong. Please try again.
        </div>
    </div>

<script>
const plans = document.querySelectorAll('.plan');
const btn = document.getElementById('payBtn');
const phone = document.getElementById('phone');
let selectedAmount = 2500;
let selectedPlan = 'starter';

plans.forEach(p => {
    p.onclick = () => {
        plans.forEach(x => x.classList.remove('selected'));
        p.classList.add('selected');
        selectedAmount = parseInt(p.dataset.amount);
        selectedPlan = p.dataset.plan;
    };
});

btn.onclick = async () => {
    const ph = phone.value.trim();
    if(!/^0[1-9][0-9]{8}$/.test(ph) && !/^254[1-9][0-9]{8}$/.test(ph)) {
        alert('Enter a valid phone number starting with 07... or 254...');
        return;
    }

    btn.disabled = true;
    document.getElementById('statusLoading').style.display = 'block';
    document.getElementById('statusSuccess').style.display = 'none';
    document.getElementById('statusError').style.display = 'none';

    try {
        const res = await fetch('/api/mpesa/pay', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: ph, amount: selectedAmount, plan: selectedPlan})
        });
        const data = await res.json();
        
        if(data.status === 'PENDING') {
            document.getElementById('statusLoading').innerHTML = 
                `✅ Prompt sent to ${ph}<br>Enter your M-Pesa PIN on your phone within 60s.`;
            
            setTimeout(async () => {
                document.getElementById('statusLoading').style.display = 'none';
                document.getElementById('statusSuccess').style.display = 'block';
            }, 15000);
        }
    } catch(e) {
        document.getElementById('statusLoading').style.display = 'none';
        document.getElementById('statusError').style.display = 'block';
    }
    
    btn.disabled = false;
};
</script>
</body>
</html>
    """)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
