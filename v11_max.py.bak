import os
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# === BASIC ROUTES ===
@app.route('/')
def home():
    return render_template_string("""
    <h1> AUREM V11 PROD LIVE</h1>
    <p>Build fixed. Render OK.</p>
    <p><a href='/dash'>/dash</a> | <a href='/b2c_test/0716706708'>/b2c_test</a> | <a href='/health'>/health</a></p>
    """)

@app.route('/health')
def health():
    return jsonify(status="ok", env=os.getenv("MPESA_ENV","unknown"))

@app.route('/dash')
def dash():
    return render_template_string("<h1>V11 Dashboard</h1><p>Prod running on Render Singapore</p>")

@app.route('/b2c_test/<phone>')
def b2c_test(phone):
    return jsonify(status="B2C route ready", phone=phone, message="Wire real cert next")

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get('hub.challenge','')
    return jsonify(status="webhook ok")

# Only run ngrok locally, NEVER on Render
if __name__ == '__main__':
    is_render = os.getenv('RENDER') is not None
    if not is_render:
        try:
            from pyngrok import ngrok
            ngrok.connect(5000)
            print("Ngrok local")
        except: pass
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',10000)))
