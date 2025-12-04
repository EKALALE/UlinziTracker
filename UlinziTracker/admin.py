from django.contrib import admin
from .models import Profile, Incident

# Admin for Incident model
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'status', 'time_reported', 'location')
    list_filter = ('status', 'time_reported')
    search_fields = ('title', 'description', 'reporter__username', 'location')
    ordering = ('-time_reported',)

# Admin for Profile model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'contact_number', 'location')
    list_filter = ('role',)
    search_fields = ('user__username', 'contact_number', 'location')

# Register models
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Incident, IncidentAdmin)
