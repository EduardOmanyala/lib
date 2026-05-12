from django.contrib import admin
from .models import ContactMessage, PostContent, Posts

# Register your models here.
admin.site.register(ContactMessage)
admin.site.register(Posts)
admin.site.register(PostContent)