from django.urls import path
from app.views import (
    roles_table,
    roles_create,
    roles_update,
    roles_save,
    roles_delete,
)

urlpatterns = [
    path("", view=roles_table, name="roles_table"),
    path("create/", view=roles_create, name="roles_create"),
    path("update/<int:role_id>/", view=roles_update, name="roles_update"),
    path("save/", view=roles_save, name="roles_save"),
    path("delete/<int:role_id>/", view=roles_delete, name="roles_delete"),
]
