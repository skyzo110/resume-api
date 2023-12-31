from django.contrib import admin
from .models import Opportunity, Applicant, Application, HR, Document, User, SortApplication

admin.site.register(Opportunity)
admin.site.register(Applicant)
admin.site.register(Application)
admin.site.register(SortApplication)
admin.site.register(HR)
admin.site.register(Document)

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    pass