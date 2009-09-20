import logging, os, sys, models
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

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
        self.response.out.write("{'code': 0, 'value': %d}" % device.id)

class DevUnRegisterHandler(webapp.RequestHandler):
    def get(self, device_token):
        device, newcreated  = models.get_or_create_device(device_token)
        self.redirect("/devices/")

class DevNotifyHandler(webapp.RequestHandler):
    def get(self, device_id):
        device, newcreated  = models.get_or_create_device(device_token)
        self.redirect("/devices/")

class DevDetailsHandler(webapp.RequestHandler):
    def get(self, device_id):
        device = models.Device.all().filter("id = ", device_id)
        if device.count() > 0:
            render_template(self, "details.html", {'device': device})
        else:
            self.error(404)
            self.response.out.write("Invalid device id")

def main():
    application = webapp.WSGIApplication(
        [
            ('/devices/register/.*/', DevRegisterHandler),
            ('/devices/unregister/.*/', DevUnRegisterHandler),
            ('/devices/.*/notify', DevNotifyHandler),
            ('/devices/.*/', DevDetailsHandler),
            ('/devices/', DevListHandler),
            ('/', MainPage),
        ],
        debug = True)

    # run it
    from google.appengine.ext.webapp import util
    util.run_wsgi_app(application)

if __name__ == "__main__": main()

