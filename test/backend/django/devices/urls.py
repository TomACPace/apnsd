
from django.conf import settings
from django.conf.urls.defaults import *

import views

urlpatterns = patterns ('',
    url(r'^$', views.list_devices, name = "list_devices"),
    url(r'^register/(?P<device_token>[^/]+)/$', views.register_device, name = "register_device"),
    url(r'^unregister/(?P<device_token>[^/]+)/$', views.unregister_device, name = "unregister_device"),
    url(r'^(?P<device_id>[^/]+)/$', views.device_details, name = "device_details"),
    url(r'^(?P<device_id>[^/]+)/notify/$', views.notify_device, name = "notify_device"),
)

