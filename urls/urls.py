from django.urls import path
from views import index_view

urlpatterns = [
    path("", view=index_view, name="index"),
]
