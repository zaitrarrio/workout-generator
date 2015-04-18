from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from .basic_navigation import views
from .basic_navigation import api

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^mygoalsnew/$', views.redirect),
    url(r'^confirm/(?P<confirmation_code>\w+)/', views.confirm, name='confirm'),
    url(r'^api/signup/', api.signup, name="signup"),
    url(r'^api/goals/', api.goals, name="goals"),
    url(r'^api/equipment/', api.equipment, name="equipment"),
    url(r'^api/user/', api.user, name="user"),
    url(r'^api/payment/', api.payment, name="user"),
    url(r'^api/cancel_payment/', api.cancel_payment, name="cancel-payment"),
    url(r'^api/workout/', api.workout, name="workout"),
    url(r'^api/coupon/(?P<coupon_code>\w+)/', api.coupon, name="coupon"),
    url(r'^api/re_send_confirmation/', api.re_send_confirmation, name="re-send-confirmation"),
    url(r'^api/re_send_confirmation/', api.re_send_confirmation, name="re-send-confirmation"),
    url(r'^api/text_link/', api.text_link, name="text-link"),
    (r'^backstage/', include('workout_generator.backstage.urls')),
)
