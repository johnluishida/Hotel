from flask import Flask

app = Flask(__name__)
app.secret_key = 'your_secret_key'

from main.moon_routes import moon_routes

app.register_blueprint(moon_routes)