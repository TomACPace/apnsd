from google.appengine.ext import db
import datetime

# 
# A simple non-sharded device counter
#
class DeviceCounter(db.Model):
    app_name        = db.StringProperty(default = "")
    num_devices     = db.IntegerProperty(default = 0)

class Device(db.Model):
    # An integer ID 
    id              = db.IntegerProperty(default = 0)

    # The unique device ID/token that is registered
    device_token    = db.StringProperty()

    # When was the device registered
    created         = db.DateTimeProperty(auto_now_add = True)

    # Status of a device
    status          = db.IntegerProperty(default = 0)

def increment_device_counter():
    dev_counter = DeviceCounter.all().filter("app_name = ", "apnstest")
    if dev_counter.count() == 0:
        dev_counter = DeviceCounter(app_name = "apnstest", num_devices = 1)
    else:
        dev_counter = dev_counter.fetch(1)[0]
        dev_counter.num_devices += 1
    db.put(dev_counter)

def get_or_create_device(device_token):
    device = Device.filter('device_token = ', device_token)
    if device.count() == 0:
        device = models.Device(device_token = device_token,
                               id = increment_device_counter())
        db.put(device)
        return device, True
    else:
        return device.fetch(1)[0], False

