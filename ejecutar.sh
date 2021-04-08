#gunicorn -k gevent -w 2 app:app
gunicorn --worker-class gevent --workers 1 --bind 127.0.0.1:8000 app:app 
#gunicorn --threads 50 --workers 1 --bind 127.0.0.1:8000 app:app
