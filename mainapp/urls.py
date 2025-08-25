from django.urls import path
from .views import index, store

urlpatterns = [
    path('2', index),
    path('s', store)
]


