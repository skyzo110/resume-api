from django.contrib import admin
from .models import Opportunity, Applicant, Application

admin.site.register(Opportunity)
admin.site.register(Applicant)
admin.site.register(Application)