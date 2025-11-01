import os
from app import app

# Create application alias for Vercel
application = app

if __name__ == "__main__":
    app.run()
