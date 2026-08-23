import os, requests, datetime
from dotenv import load_dotenv
load_dotenv()
BASE="https://sandbox.safaricom.co.ke" if os.getenv("MPESA_ENV","sandbox")=="sandbox" else "https://api.safaricom.co.ke"
def get_token():
    r=requests.get(f"{BASE}/oauth/v1/generate?grant_type=client_credentials", auth=(os.getenv("MPESA_CONSUMER_KEY"),os.getenv("MPESA_CONSUMER_SECRET")), timeout=10)
    return r.json().get("access_token")
def b2c_send(phone, amount=1000, remarks="AUREM REF 1k"):
    phone=''.join(filter(str.isdigit, phone))
    if phone.startswith("0"): phone="254"+phone[1:]
    token=get_token()
    if not token or "PASTE" in os.getenv("MPESA_CONSUMER_KEY","PASTE"):
        open("logs/b2c_mock.csv","a").write(f"{datetime.datetime.now().isoformat()},{phone},{amount},MOCK\n")
        print(f"[B2C MOCK] {phone} {amount}")
        return {"ResultCode":"0","mock":True}
    payload={"InitiatorName":os.getenv("MPESA_INITIATOR"),"SecurityCredential":os.getenv("MPESA_SECURITY_CRED"),"CommandID":"BusinessPayment","Amount":int(amount),"PartyA":os.getenv("MPESA_SHORTCODE","174379"),"PartyB":phone,"Remarks":remarks,"QueueTimeOutURL":f"https://{os.getenv('NGROK_DOMAIN')}/b2c_timeout","ResultURL":f"https://{os.getenv('NGROK_DOMAIN')}/b2c_result","Occassion":"Referral"}
    try:
        r=requests.post(f"{BASE}/mpesa/b2c/v1/paymentrequest", json=payload, headers={"Authorization":f"Bearer {token}"}, timeout=15)
        open("logs/b2c_real.csv","a").write(f"{datetime.datetime.now().isoformat()},{phone},{amount},{r.text[:200]}\n")
        print(f"[B2C REAL] {phone} -> {r.text[:100]}")
        return r.json()
    except Exception as e: return {"error":str(e)}
