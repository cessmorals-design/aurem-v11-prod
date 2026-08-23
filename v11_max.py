import os, requests, base64, json, time
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# ENV
MPESA_ENV = os.getenv("MPESA_ENV","production")
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
SHORTCODE = os.getenv("MPESA_SHORTCODE")
PASSKEY = os.getenv("MPESA_PASSKEY")
B2C_INITIATOR = os.getenv("MPESA_B2C_INITIATOR")
B2C_PASSWORD = os.getenv("MPESA_B2C_PASSWORD")
B2C_SHORTCODE = os.getenv("MPESA_B2C_SHORTCODE", SHORTCODE)

BASE_URL = "https://api.safaricom.co.ke" if MPESA_ENV=="production" else "https://sandbox.safaricom.co.ke"

def get_token():
    if not CONSUMER_KEY: return None
    auth = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
    r = requests.get(f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials", headers={"Authorization": f"Basic {auth}"}, timeout=15)
    return r.json().get("access_token")

@app.route('/')
def home():
    return render_template_string("""
    <style>body{font-family:sans-serif;text-align:center;padding:40px} .btn{padding:12px 24px;background:#00d632;color:white;border-radius:8px;text-decoration:none}</style>
    <h1>AUREM V11  PRODUCTION LIVE </h1>
    <p>Render Singapore | {{env}} | {{time}}</p>
    <p><a class=btn href='/dash'>Open Dashboard</a></p>
    <p><a href='/health'>/health</a>  <a href='/b2c_test/0716706708'>Test B2C 1k</a></p>
    """, env=MPESA_ENV, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/health')
def health():
    return jsonify(status="ok", env=MPESA_ENV, shortcode=SHORTCODE, has_token=bool(CONSUMER_KEY), timestamp=datetime.now().isoformat())

@app.route('/dash')
def dash():
    return render_template_string("""
    <h1>V11 DASH  PROD</h1>
    <ul>
    <li>Env: {{env}}</li>
    <li>Shortcode: {{sc}}</li>
    <li>B2C Initiator: {{init}}</li>
    <li>Base: {{base}}</li>
    </ul>
    <p>Endpoints: /stk_push, /b2c_test/&lt;phone&gt;, /webhook, /mpesa/callback</p>
    """, env=MPESA_ENV, sc=SHORTCODE, init=B2C_INITIATOR, base=BASE_URL)

@app.route('/stk_push', methods=['POST'])
def stk_push():
    data = request.json or {}
    phone = data.get('phone','0716706708')
    amount = data.get('amount',1)
    token = get_token()
    if not token: return jsonify(error="no token, check CONSUMER_KEY"),500
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    pwd = base64.b64encode(f"{SHORTCODE}{PASSKEY}{ts}".encode()).decode()
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": pwd,
        "Timestamp": ts,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": f"https://aurem-v11-prod.onrender.com/mpesa/callback",
        "AccountReference": "AUREM",
        "TransactionDesc": "AUREM Test"
    }
    r = requests.post(f"{BASE_URL}/mpesa/stkpush/v1/processrequest", json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=15)
    return jsonify(r.json())

@app.route('/b2c_test/<phone>')
def b2c_test(phone):
    token = get_token()
    if not token: return jsonify(error="No token, set MPESA env vars on Render", env=MPESA_ENV)
    # NOTE: For prod B2C you need SecurityCredential (cert). This will return error until cert added  that's expected.
    payload = {
        "InitiatorName": B2C_INITIATOR,
        "SecurityCredential": B2C_PASSWORD or "PLACEHOLDER_NEEDS_CERT",
        "CommandID": "BusinessPayment",
        "Amount": 10,
        "PartyA": B2C_SHORTCODE,
        "PartyB": phone,
        "Remarks": "AUREM Test 10",
        "QueueTimeOutURL": "https://aurem-v11-prod.onrender.com/mpesa/b2c_timeout",
        "ResultURL": "https://aurem-v11-prod.onrender.com/mpesa/b2c_result",
        "Occasion": "Test"
    }
    r = requests.post(f"{BASE_URL}/mpesa/b2c/v3/paymentrequest", json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=15)
    return jsonify(request=r.json(), note="If 'Invalid SecurityCredential' -> need cert generation next")

@app.route('/mpesa/callback', methods=['POST'])
def mpesa_cb():
    print("MPESA CALLBACK", request.json)
    return jsonify(ResultCode=0, ResultDesc="ok")

@app.route('/mpesa/b2c_result', methods=['POST'])
def b2c_result():
    print("B2C RESULT", request.json)
    return jsonify(ResultCode=0, ResultDesc="ok")

@app.route('/mpesa/b2c_timeout', methods=['POST'])
def b2c_timeout():
    print("B2C TIMEOUT", request.json)
    return jsonify(ResultCode=0, ResultDesc="ok")

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method=='GET':
        return request.args.get('hub.challenge','ok')
    return jsonify(status="webhook received")

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT",10000)))
