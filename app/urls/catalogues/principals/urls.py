from django.urls import path
from app.views import (
    principals_table,
    principals_create,
    principals_update,
    principals_save,
    principals_delete,
)

urlpatterns = [
    path('', view=principals_table, name='principals_table'),
    path('create/', view=principals_create, name='principals_create'),
    path('update/<int:principal_id>/', view=principals_update, name='principals_update'),
    path('save/', view=principals_save, name='principals_save'),
    path('delete/<int:principal_id>/', view=principals_delete, name='principals_delete'),
]
