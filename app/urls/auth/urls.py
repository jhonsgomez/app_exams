from django.urls import path
from app.views.auth.views import login, register, logout

urlpatterns = [
    path("login/", view=login, name="auth_login"),
    path("register/", view=register, name="auth_register"),
    path("logout/", view=logout, name="auth_logout"),
]
