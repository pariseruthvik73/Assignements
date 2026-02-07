from flask import Flask, jsonify
import random

app = Flask(__name__)

# List of jokes
jokes = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why do Java developers wear glasses? Because they don't C#!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    "Why did the developer go broke? Because he used up all his cache!",
    "What's a programmer's favorite place? Foo Bar!",
    "Why do Python programmers prefer snake_case? Because they can't C!",
    "Docker containers are like apartments: isolated, but they share the same building!",
]

@app.route('/')
def home():
    return jsonify({"message": "Backend API is running!", "endpoints": ["/joke"]})

@app.route('/joke')
def get_joke():
    joke = random.choice(jokes)
    return jsonify({"joke": joke})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)