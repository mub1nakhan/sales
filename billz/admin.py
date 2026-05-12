from django.contrib import admin
from billz.models import CashRegister, CashSession, CustomerGroup

admin.site.register(CashRegister)
admin.site.register(CashSession)
admin.site.register(CustomerGroup)

