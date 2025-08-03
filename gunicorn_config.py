import os

workers = int(os.environ.get('GUNICORN_PROCESSES', '2'))

threads = int(os.environ.get('GUNICORN_THREADS', '4'))

timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))

# Azure Web App uses PORT environment variable
port = os.environ.get('PORT', '8000')
bind = f"0.0.0.0:{port}"

forwarded_allow_ips = '*'

secure_scheme_headers = {'X-Forwarded-Proto': 'https'}
