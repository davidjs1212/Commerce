from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid , Comment
from django.contrib.auth.decorators import login_required
from .forms import ListingForm, BidForm


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {"listings": listings})


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
    bid_form = BidForm()
    if request.method == "POST":
        if request.user.is_authenticated:

            if request.POST.get("action") == "bid" and listing.active:
                bid_form = BidForm(request.POST)
                if bid_form.is_valid():
                    amount = bid_form.cleaned_data["amount"]
                    current = listing.current_price()
                    if amount < listing.starting_bid:
                        message = f"Your bid must be at least ${listing.starting_bid}"
                        return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bid_form": bid_form,
                        "message": message,
                        "current_price": current
                        })
                    elif amount <= current:
                        message = f"Your bid must be higher than ${current}"
                        return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bid_form": bid_form,
                        "message": message,
                        "current_price": current
                    })

                    else:
                        Bid.objects.create(
                            listing=listing,
                            bidder=request.user,
                            amount=amount
                        )
                        return HttpResponseRedirect(reverse("listing", args=[listing.id]))

        else:
            return HttpResponseRedirect(reverse("login"))

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": bid_form,
        "current_price": listing.current_price(),
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
