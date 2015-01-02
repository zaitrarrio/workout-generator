from django.conf.urls import patterns, url

from .basic_navigation.views import home
from .basic_navigation import api

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^api/signup/', api.signup, name="signup"),
    url(r'^api/goals/', api.goals, name="goals"),
)
