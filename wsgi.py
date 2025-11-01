import os
from app import app

# Create application alias for Vercel
application = app

# Initialize database on first request
@app.before_request
def initialize_database():
    """Initialize database tables on first request in serverless environment"""
    if os.environ.get('VERCEL'):
        from app import init_db
        try:
            init_db()
        except Exception:
            pass  # Tables already exist
        # Remove this hook after first run
        app.before_request_funcs[None].remove(initialize_database)

if __name__ == "__main__":
    app.run()
