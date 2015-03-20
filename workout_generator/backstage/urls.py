from django.conf.urls import patterns
from django.conf.urls import url

from .views import BackstageViews

urlpatterns = patterns('',
    url(r'^$', BackstageViews.home, name='backstage-home'),
    url(r'^user/(?P<user_id>\d+)/', BackstageViews.user, name='backstage-user'),
)
