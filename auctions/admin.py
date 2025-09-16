from django.contrib import admin

from .models import User, Listing, Bid, Comment
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "active", "starting_bid", "current_price", "winner", "category", "created")
    list_filter = ("active", "category")
    search_fields = ("title", "description")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "bidder", "amount", "placed_at")
    search_fields = ("listing__title", "bidder__username")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "author", "created_at")
    search_fields = ("listing__title", "author__username")

admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Listing, ListingAdmin)