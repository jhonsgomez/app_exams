from django.urls import path
from app.views import (
    representatives_table,
    representatives_create,
    representatives_update,
    representatives_save,
    representatives_delete,
)

urlpatterns = [
    path("", representatives_table, name="representatives_table"),
    path("create/", representatives_create, name="representatives_create"),
    path("update/<int:representative_id>/", representatives_update, name="representatives_update"),
    path("save/", representatives_save, name="representatives_save"),
    path("delete/<int:representative_id>/", representatives_delete, name="representatives_delete"),
]
