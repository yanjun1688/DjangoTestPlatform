from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import TestCase, TestPlan

# Register your models here.
admin.site.register(TestCase, DraggableMPTTAdmin)
admin.site.register(TestPlan)
