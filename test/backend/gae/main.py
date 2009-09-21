import logging, os, sys, models

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson
from django.utils.simplejson import decoder
from django.utils.simplejson.encoder import JSONEncoder as jenc
from django.utils.simplejson.decoder import JSONDecoder as jdec

import apnsd
import apnsd.connectors
from apnsd.connectors import http

httpClient = http.HttpClient("sri.panyam@gmail.com", "netpass1",
                             "apnstest", "development", "http://sripanyam.org")

def get_var(request, variable, default_val = ""):
    if request.GET and variable in request.GET:
        return request.GET[variable]
    elif request.POST and variable in request.POST:
        return request.POST[variable]
    else:
        return default_val

def get_getvar(request, variable, default_val = ""):
    if request.GET and variable in request.GET:
        return request.GET[variable]
    return default_val


def get_postvar(request, variable, default_val = ""):
    if request.POST and variable in request.POST:
        return request.POST[variable]
    return default_val

def render_template(page, template_file, template_values = {}):
    path = os.path.join(os.path.dirname(__file__), "templates/" + template_file)
    page.response.out.write(template.render(path, template_values))

class MainPage(webapp.RequestHandler):
    def get(self):
        render_template(self, "index.html")

class DevListHandler(webapp.RequestHandler):
    def get(self):
        devices = models.Device.all()
        render_template(self, "devices.html",
                        {'registered_devices': devices.fetch(1000)})

class DevRegisterHandler(webapp.RequestHandler):
    def get(self, device_token):
        device, newcreated  = models.get_or_create_device(device_token)
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write("{'code': 0, 'value': %d}" % device.device_id)

class DevUnRegisterHandler(webapp.RequestHandler):
    def get(self, device_token):
        device, newcreated  = models.get_or_create_device(device_token)
        self.redirect("/devices/")

class DevNotifyHandler(webapp.RequestHandler):
    def post(self, device_id):
        device = models.get_device_by_id(device_id)

        if not device:
            self.error(404)
            self.response.out.write("Invalid device id")
            return 

        body        = self.request.body
        devtoken    = device.device_token
        aps         = {"alert":str(body)}
        alert       = self.request.get("alert")
        badge       = self.request.get("badge")
        if badge: aps["badge"] = int(badge)
        sound       = self.request.get("sound")
        if sound: aps["sound"] = sound
        print >> sys.stderr, "Alert: ", alert

        payload     = jenc().encode({"aps": aps})
        # code, value = httpClient.sendRawMessage(devtoken, payload)
        code, value = httpClient.sendSimpleMessage(devtoken, badge, sound)
        # code, value = 0, "Successfull"

        return render_template(self, "details.html",
                                  {'device': device,
                                   'notif_result': value})


class DevDetailsHandler(webapp.RequestHandler):
    def get(self, device_id):
        device = models.get_device_by_id(device_id)
        if device:
            render_template(self, "details.html", {'device': device})
        else:
            self.error(404)
            self.response.out.write("Invalid device id")

def main():
    application = webapp.WSGIApplication(
        [
            ('/devices/register/(.*)/', DevRegisterHandler),
            ('/devices/unregister/(.*)/', DevUnRegisterHandler),
            ('/devices/(.*)/notify/', DevNotifyHandler),
            ('/devices/(.*)/', DevDetailsHandler),
            ('/devices/', DevListHandler),
            ('/', MainPage),
        ],
        debug = True)

    # run it
    from google.appengine.ext.webapp import util
    util.run_wsgi_app(application)

if __name__ == "__main__": main()

