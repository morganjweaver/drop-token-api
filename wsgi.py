from api import app

# This is the WSGI entrypoint for concurrency
# Initiate the app with `gunicorn --bind 127.0.0.1:8000 wsgi`

if __name__ == "__main__":
    app.run()