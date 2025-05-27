from django.urls import path
from . import views

app_name = 'fields'  # namespace for reversing URLs

urlpatterns = [
    path('', views.field_list, name='field_list'),                 # List view
    path('create/', views.field_create, name='field_create'),      # Create view
    path('update/<int:field_id>/', views.field_update, name='field_update'),  # Update view
    path('delete/<int:field_id>/', views.field_delete, name='field_delete'),  # Delete view
]
