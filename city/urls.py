from django.urls import path
from . import views

urlpatterns = [
    path("name-city/", views.name_city, name="name-city"),
]
