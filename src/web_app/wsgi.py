# src/web_app/wsgi.py
import os
import sys

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app

if __name__ == "__main__":
    app.run()