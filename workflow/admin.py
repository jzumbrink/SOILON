from django.contrib import admin
from .models import *
from .config import production

admin.site.register(Kunde)
admin.site.register(Auftrag)
admin.site.register(Bodenprobe)
admin.site.register(PpmValue)
if not production:
    admin.site.register(Address)