from django.conf.urls import patterns, url

from .basic_navigation.views import home
from .basic_navigation import api

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^api/signup/', api.signup, name="signup"),
    url(r'^api/goals/', api.goals, name="goals"),
    url(r'^api/equipment/', api.equipment, name="equipment"),
    url(r'^api/user/', api.user, name="user"),
    url(r'^api/payment/', api.payment, name="user"),
    url(r'^api/cancel_payment/', api.cancel_payment, name="cancel-payment"),
    url(r'^api/workout/', api.workout, name="workout"),
)
