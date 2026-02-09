from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- HYBRID PERSISTENCE LOGIC ---
# Detects if running in Docker to use the Volume path, otherwise uses local folder
if os.environ.get('DOCKER_CONTAINER') == 'true':
    db_dir = '/app/data'
else:
    db_dir = os.path.join(os.getcwd(), 'data')

# Ensure the directory exists to avoid PermissionErrors
os.makedirs(db_dir, exist_ok=True)

db_path = os.path.join(db_dir, 'blog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)

# Create tables within the app context
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return {
        "status": "online",
        "message": "Welcome to the Blog API",
        "endpoints": {
            "get_posts": "/posts (GET)",
            "create_post": "/posts (POST)",
            "health_check": "/health"
        }
    }

@app.route('/health')
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({"error": "Missing title or content"}), 400
        new_post = Post(title=data['title'], content=data['content'])
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"message": "Post created!"}), 201
    posts = Post.query.all()
    return jsonify([{"id": p.id, "title": p.title, "content": p.content} for p in posts])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)