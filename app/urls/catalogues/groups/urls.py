from django.urls import path
from app.views import (
    groups_table,
    groups_create,
    groups_update,
    groups_save,
    groups_delete,
)

urlpatterns = [
    path("", groups_table, name="groups_table"),
    path("create/", groups_create, name="groups_create"),
    path("update/<int:group_id>/", groups_update, name="groups_update"),
    path("save/", groups_save, name="groups_save"),
    path("delete/<int:group_id>/", groups_delete, name="groups_delete"),
]
