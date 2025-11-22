from django.urls import path
from app.views import (
    modalities_table,
    modalities_create,
    modalities_update,
    modalities_save,
    modalities_delete
)

urlpatterns = [
    path('', view=modalities_table, name='modalities_table'),
    path('create/', view=modalities_create, name='modalities_create'),
    path('update/<int:modality_id>/', view=modalities_update, name='modalities_update'),
    path('save/', view=modalities_save, name='modalities_save'),
    path('delete/<int:modality_id>/', view=modalities_delete, name='modalities_delete'),
]
