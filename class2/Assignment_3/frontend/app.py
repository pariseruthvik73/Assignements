from flask import Flask, render_template_string
import requests
import os

app = Flask(__name__)

# Backend API URL - uses container name on custom network
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend-api:5000')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Joke App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
        }
        .joke-box {
            background-color: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            margin: 30px 0;
            min-height: 100px;
            font-size: 18px;
            line-height: 1.6;
        }
        button {
            background-color: #667eea;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 20px auto;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
        }
        button:hover {
            background-color: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        .error {
            color: #dc3545;
            padding: 20px;
            background-color: #f8d7da;
            border-radius: 10px;
            border-left: 5px solid #dc3545;
        }
        .info {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Random Joke Generator</h1>
        <div class="joke-box">
            {% if error %}
                <div class="error">{{ error }}</div>
            {% else %}
                <p>{{ joke }}</p>
            {% endif %}
        </div>
        <button onclick="location.reload()">Get Another Joke 🔄</button>
        <div class="info">
            <p>Frontend Container → Backend Container Communication</p>
            <p>Connected via: {{ backend_url }}</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    try:
        # Call backend API to get a joke
        response = requests.get(f'{BACKEND_URL}/joke', timeout=5)
        response.raise_for_status()
        data = response.json()
        joke = data.get('joke', 'No joke found!')
        error = None
    except requests.exceptions.ConnectionError:
        joke = None
        error = f"❌ Cannot connect to backend at {BACKEND_URL}. Make sure both containers are on the same network!"
    except requests.exceptions.Timeout:
        joke = None
        error = "⏱️ Backend timeout. The backend is taking too long to respond."
    except Exception as e:
        joke = None
        error = f"❌ Error: {str(e)}"
    
    return render_template_string(HTML_TEMPLATE, joke=joke, error=error, backend_url=BACKEND_URL)

@app.route('/health')
def health():
    return {"status": "healthy", "backend": BACKEND_URL}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)