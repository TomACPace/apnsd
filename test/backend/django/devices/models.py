from django.db import models
import datetime

class Device(models.Model):
    # The unique device ID/token that is registered
    device_token    = models.CharField(max_length = 64)

    # When was the booking made?
    created         = models.DateTimeField(auto_now_add = True)

    # Status of a booking
    status          = models.IntegerField(default = 0)

    class Admin: save_on_top = True

#################   Register Models with Admin ####################

from django.contrib import admin as djangoadmin
djangoadmin.site.register(Device)

