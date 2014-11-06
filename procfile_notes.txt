web: gunicorn one_rep_max.wsgi --log-file -;
worker: celeryd -l info
