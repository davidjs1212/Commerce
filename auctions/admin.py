from django.contrib import admin

from .models import User, Listing, Bid, Comment

# Register your models here.
admin.site.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "active", "category", "created")
    list_filter = ("active", "category")
    search_fields = ("title", "description")

admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Comment)