from django.urls import path
from app.views import (
    knowledge_table,
    knowledge_create,
    knowledge_update,
    knowledge_save,
    knowledge_delete,
)

urlpatterns = [
    path("", knowledge_table, name="knowledge_table"),
    path("create/", knowledge_create, name="knowledge_create"),
    path("update/<int:knowledge_area_id>/", knowledge_update, name="knowledge_update"),
    path("save/", knowledge_save, name="knowledge_save"),
    path("delete/<int:knowledge_area_id>/", knowledge_delete, name="knowledge_delete"),
]
