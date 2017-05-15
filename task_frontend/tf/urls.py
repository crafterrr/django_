from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
from django.conf.urls import include

urlpatterns = {
    url(r'^login/$', login, name="login"),
    url(r'^logout/$', log_out, name="logout"),
    url(r'^register/$', register, name="register"),
    url(r'^todolists/$', lists_view, name="lists"),
    url(r'^todolists/shared/(?P<pk>[0-9]+)/$', list_shared_details_view, name="list-shared-details"),
    url(r'^todolists/create/$', list_create_view, name="list-create"),
    url(r'^todolists/(?P<pk>[0-9]+)/$', list_edit_view, name="list-detail"),
    url(r'^todolists/(?P<pk>[0-9]+)/share/$', list_share_view, name="list-share"),
    url(r'^todolists/(?P<pk>[0-9]+)/delete/$', list_delete, name="list-delete"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/$', list_details_view, name="tasks"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/create/$', task_create_view, name="task-create"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/$', task_details_view, name="task-detail"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/delete/$', task_delete, name="task-delete"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/edit/$', task_edit_view, name="task-edit"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
