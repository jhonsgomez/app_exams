from django.urls import path
from app.views import (
    admins_table,
    admins_create,
    admins_update,
    admins_save,
    admins_delete,
    admins_activate,
    admins_deactivate,
)

urlpatterns = [
    path("", admins_table, name="admins_table"),
    path("create/", admins_create, name="admins_create"),
    path("update/<int:admin_id>/", admins_update, name="admins_update"),
    path("save/", admins_save, name="admins_save"),
    path("delete/<int:admin_id>/", admins_delete, name="admins_delete"),
    path("activate/<int:admin_id>/", admins_activate, name="admins_activate"),
    path("deactivate/<int:admin_id>/", admins_deactivate, name="admins_deactivate"),
]
