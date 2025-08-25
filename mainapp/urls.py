from django.urls import path
from .views import index

urlpatterns = [
    path('/2', index),
]


