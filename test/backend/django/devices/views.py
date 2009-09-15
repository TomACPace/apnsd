# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.utils.simplejson import decoder
import  sys, logging, datetime, models

import apnsd
import apnsd.clients
from    apnsd.clients import line
lineClient = line.LineClient()

bundle_id = "apnstest"

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


class OurJsonEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if type(o) is datetime.datetime:
            return str(o)
        return super(OurJsonEncoder, self).default(o)

# 
# Generates an api output structure indicating success
#
def api_result(code, value):
    return {'code': code, 'value': value}

def json_encode(data):
    return OurJsonEncoder().encode(data)

def json_decode(data):
    if data:
        from django.utils.simplejson.decoder import JSONDecoder as jdec
        return jdec().decode(data)
    else:
        return None

def register_device(request, device_token):
    device, newcreated  = models.Device.objects.get_or_create(device_token = device_token)
    return HttpResponse(json_encode(api_result(0, {'device': device.id})))

def unregister_device(request, device_token):
    try:
        if request.GET and 'is_token' in request.GET and request.GET['is_token']:
            device = models.Device.objects.get(pk = device_token)
        else:
            device = models.Device.objects.get(device_token = device_token)
        device.delete()
    except models.Device.DoesNotExist:
        pass
    return HttpResponseRedirect("/devices/")

def list_devices(request):
    devices = models.Device.objects.all()
    return render_to_response("devices.html",
                               {'registered_devices': devices})

def device_details(request, device_id):
    try:
        device = models.Device.objects.get(pk = device_id)
        return render_to_response("details.html",
                                   {'device': device})
    except models.Device.DoesNotExist:
        return HttpResponseRedirect("/devices/")

def notify_device(request, device_id):
    if request.method == "POST":
        try:
            device      = models.Device.objects.get(pk = device_id)
            devtoken    = device.device_token
            aps         = {"alert":str(request.POST['payload'])}
            badge       = get_var(request, "badge", None)
            if badge: aps["badge"] = int(badge)
            sound       = get_var(request, "sound", None)
            if sound: aps["sound"] = sound

            payload     = json_encode({"aps": aps})
            code, value = lineClient.sendMessage(bundle_id, devtoken, payload)
            # code, value = 0, "Successfull"

            return render_to_response("details.html",
                                      {'device': device,
                                       'notif_result': value})
        except models.Device.DoesNotExist:
            pass

    return HttpResponseRedirect("/devices/")

