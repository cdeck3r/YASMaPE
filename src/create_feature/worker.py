from celery import Celery

# apply celeryconfig.py as configuration
app = Celery(include=['tasks'])
app.config_from_object('celeryconfig')

if __name__ == '__main__':
    app.start()
