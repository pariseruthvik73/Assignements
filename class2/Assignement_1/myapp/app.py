from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.get('/')
def home():
    # Your details
    name = "Ruthvik Parise"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    movies = ["Inception", "The Dark Knight", "Interstellar", "The Prestige"]

    # Creating a simple HTML string to display
    movie_list_html = "".join([f"<li>{movie}</li>" for movie in movies])
    
    return f"""
    <h1>DevOps Bootcamp Project</h1>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Current Date & Time:</strong> {now}</p>
    <h3>Favorite Movies:</h3>
    <ul>
        {movie_list_html}
    </ul>
    """

if __name__ == '__main__':
    # Using 0.0.0.0 is crucial for Docker to communicate with the host
    app.run(host='0.0.0.0', port=5000)
    