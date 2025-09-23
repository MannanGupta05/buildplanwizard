from flask import Flask
import os
import sys

# Handle both relative and absolute imports
try:
    from .routes import register_routes
    from .database import init_db
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from routes import register_routes
    from database import init_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key_change_this_in_production")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the database
init_db()

# Register all Flask routes
register_routes(app)

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)

