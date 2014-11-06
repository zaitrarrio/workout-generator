import django

from celery import platforms
from celery.signals import worker_process_init
from celery.task import task


@task
def do_anything():
    print "delete me"


def cleanup_after_tasks(signum, frame):
    django.setup()


def install_pool_process_sighandlers(**kwargs):
    platforms.signals["TERM"] = cleanup_after_tasks
    platforms.signals["INT"] = cleanup_after_tasks

worker_process_init.connect(install_pool_process_sighandlers)
