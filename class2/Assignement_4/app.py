from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/')
def home():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Test App</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
            }}
            .container {{
                background-color: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }}
            h1 {{
                color: #1e3c72;
                text-align: center;
            }}
            .info-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 5px solid #1e3c72;
            }}
            .info-item {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
            }}
            .info-item:last-child {{
                border-bottom: none;
            }}
            .label {{
                font-weight: bold;
                color: #555;
            }}
            .value {{
                color: #1e3c72;
                font-family: monospace;
            }}
            .network-mode {{
                text-align: center;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                margin: 20px 0;
                font-size: 20px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Docker Network Test Application</h1>
            <div class="network-mode">
                Network Mode: {os.getenv('NETWORK_MODE', 'Unknown')}
            </div>
            <div class="info-box">
                <div class="info-item">
                    <span class="label">Container Hostname:</span>
                    <span class="value">{hostname}</span>
                </div>
                <div class="info-item">
                    <span class="label">Container IP Address:</span>
                    <span class="value">{ip_address}</span>
                </div>
                <div class="info-item">
                    <span class="label">Flask Port:</span>
                    <span class="value">5000</span>
                </div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 30px;">
                This app helps compare Docker networking modes
            </p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/info')
def info():
    return jsonify({
        'hostname': socket.gethostname(),
        'ip': socket.gethostbyname(socket.gethostname()),
        'network_mode': os.getenv('NETWORK_MODE', 'Unknown')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)