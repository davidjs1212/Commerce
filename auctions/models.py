from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django.db.models import CASCADE

class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    photo = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    watchers = models.ManyToManyField(User, related_name="watchlist", blank=True)
    
    def current_price(self):
        # Return highest bid if present, else return starting bid.
        highest = self.bids.order_by("-amount",).first()
        return highest.amount if highest else self.starting_bid

    def __str__(self):
        return f"{self.title} created by {self.owner} on {self.created}."
    
    class Meta:
        ordering = ["-created"]


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=CASCADE, related_name="placed_bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid {self.amount} by {self.bidder} at {self.placed_at}"
    
    class Meta:
        ordering = ["-placed_at"]


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=CASCADE, related_name="user_comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author}"
    
    class Meta:
        ordering = ["-created_at"]
