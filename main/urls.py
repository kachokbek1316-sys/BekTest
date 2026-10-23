from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("test/<int:test_id>/", views.take_test, name="take_test"),
    path("categories/", views.categories, name="categories"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("about/", views.about, name="about"),
]