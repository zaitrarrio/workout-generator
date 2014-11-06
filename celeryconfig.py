import os


if os.environ.get("I_AM_IN_DEV_ENV"):
    BROKER_URL = 'amqp://guest:guest@localhost//'
else:
    BROKER_URL = "amqp://nxwmvyul:5Zhb-we6IDlFPOJQAT5k2p5ePZm_IiSw@tiger.cloudamqp.com/nxwmvyul"

CELERY_IMPORTS = (
    'workout_generator.tasks',
    'workout_generator.mailgun.tasks',
)


CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 4
BROKER_CONNECTION_RETRY = True
BROKER_CONNECTION_MAX_RETRIES = 5
