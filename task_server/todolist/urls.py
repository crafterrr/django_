from django.conf.urls import url
from rest_framework.authtoken import views
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = {
    url(r'users/$', UserView.as_view(), name='users'),
    url(r'^todolists/$', TasklistCreateView.as_view(), name="lists"),
    url(r'^todolists/shared/$', TasklistSharedView.as_view(), name="shared-lists"),
    url(r'^todolists/shared/(?P<pk>[0-9]+)/$', TasklistSharedDetailsView.as_view(), name="shared-list-detail"),
    url(r'^todolists/(?P<pk>[0-9]+)/$', TasklistDetailsView.as_view(), name="list-detail"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/$', TaskCreateView.as_view(), name="tasks"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/$', TaskDetailsView.as_view(), name="task-detail"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/tags/$', TagCreateView.as_view(), name="tags"),
    url(r'^register/$', register_user, name='register'),
    url(r'^confirm/(?P<act_key>[a-z0-9]+)/$', confirm_user, name='confirm'),
    url(r'^token/', views.obtain_auth_token, name='token'),
}

urlpatterns = format_suffix_patterns(urlpatterns)
