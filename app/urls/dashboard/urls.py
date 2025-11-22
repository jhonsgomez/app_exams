from django.urls import path
from app.views import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
]
