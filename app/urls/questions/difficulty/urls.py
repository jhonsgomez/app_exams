from django.urls import path
from app.views import (
    difficulty_table,
    difficulty_create,
    difficulty_update,
    difficulty_save,
    difficulty_delete
)

urlpatterns = [
    path("", difficulty_table, name="difficulty_table"),
    path("create/", difficulty_create, name="difficulty_create"),
    path("update/<int:difficulty_level_id>/", difficulty_update, name="difficulty_update"),
    path("save/", difficulty_save, name="difficulty_save"),
    path("delete/<int:difficulty_level_id>/", difficulty_delete, name="difficulty_delete"),
]