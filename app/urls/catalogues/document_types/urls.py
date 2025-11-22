from django.urls import path
from app.views import (
    document_types_table,
    document_types_create,
    document_types_update,
    document_types_save,
    document_types_delete,
)

urlpatterns = [
    path('', view=document_types_table, name='document_types_table'),
    path('create/', view=document_types_create, name='document_types_create'),
    path('update/<int:document_type_id>/', view=document_types_update, name='document_types_update'),
    path('save/', view=document_types_save, name='document_types_save'),
    path('delete/<int:document_type_id>/', view=document_types_delete, name='document_types_delete'),
]
