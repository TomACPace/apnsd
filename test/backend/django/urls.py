from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin        as djangoadmin
djangoadmin.autodiscover()

import devices


# 
# The main page and ADMIN urls - last match
#
urlpatterns = patterns('',
    # Uncomment the following for admin:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', djangoadmin.site.root),
)

urlpatterns +=  patterns('', url(r'^devices/', include('devices.urls')))

# 
# The main top level site URL
#
urlpatterns += patterns('django.views.generic.simple',
    # Main page
    (r'^$', 'direct_to_template', {'template': "index.html"}),
)
