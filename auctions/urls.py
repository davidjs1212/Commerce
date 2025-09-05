from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("create_listing", views.create_listing, name="create"),
    path("listings/<int:listing_id>/watch/", views.toggle_watch, name="toggle_watch"),
    path("category", views.category, name="category"),
]
