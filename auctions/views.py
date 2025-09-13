from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid , Comment
from django.contrib.auth.decorators import login_required
from .forms import ListingForm, BidForm, CommentForm
from django.db.models import Max


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
        })


def closed_listings(request):
    closed_listings = Listing.objects.filter(active=False)
    return render(request, "auctions/closed_listings.html", {"closed_listings": closed_listings})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user_top_bid = None
    message = None
    bid_form = BidForm()
    comment_form = CommentForm()
    comments = listing.comments.select_related("author").all()

    if request.method == "POST" and not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    if request.user.is_authenticated:
        user_top_bid = listing.bids.filter(bidder=request.user).aggregate(Max("amount"))["amount__max"]
        if request.method == "POST":
            if request.POST.get("action") == "comment":
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                    Comment.objects.create(
                        listing=listing,
                        author = request.user,
                        body=comment_form.cleaned_data["body"]
                    )
                    return HttpResponseRedirect(reverse("listing", args=[listing.id]))
                
            elif request.POST.get("action") == "bid" and listing.active:
                if request.user == listing.owner:
                    message = "The owner cannot bid on their own listing."
                else:
                    bid_form = BidForm(request.POST)
                    current = listing.starting_bid
                    if bid_form.is_valid():
                        amount = bid_form.cleaned_data["amount"]
                        if listing.bids.exists():
                            current = listing.current_price()
                            if amount <= current:
                                message = f"Your bid must be higher than ${current}"
        
                            else:
                                Bid.objects.create(
                                    listing=listing,
                                    bidder=request.user,
                                    amount=amount
                                )
                                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
                        else:
                            # no bids yet
                            if amount < current:
                                message = f"Your bid must be at least ${current}"
                            else:
                                Bid.objects.create(
                                    listing=listing,
                                    bidder=request.user,
                                    amount=amount
                                )
                                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
                    else:
                        message = "Please enter a valid bid"


            elif request.POST.get("action") == "close" and listing.active:
                if request.user == listing.owner:
                    top_bid = listing.bids.order_by("-amount").first()
                    listing.active = False
                    if top_bid:
                        listing.winner = top_bid.bidder
                    listing.save()
                    return HttpResponseRedirect(reverse("listing",args=[listing.id]))
                else:
                    message = "Only the listing owner can close an auction."

                
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "message": message,
        "current_price": listing.current_price(),
        "has_bids": listing.bids.exists(),
        "user_top_bid": user_top_bid,
        "comments": comments,
    })




@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html",{
        "form":form
    })


@login_required
def watchlist(request):
    listings = request.user.watchlist.all().select_related("owner")
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


@login_required
def toggle_watch(request, listing_id):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("watchlist"))
    listing = Listing.objects.get(pk=listing_id)
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)
    return HttpResponseRedirect(reverse("watchlist"))


def category(request):
    categories = (
        Listing.objects.filter(active=True)
        .exclude(category__exact="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
    return render(request, "auctions/category.html", {
        "categories": categories,
    })


def category_listing(request, category):
    listings = Listing.objects.filter(active=True, category__iexact=category)
    return render(request, "auctions/category_listing.html", {
        "category": category,
        "listings": listings,
    })
