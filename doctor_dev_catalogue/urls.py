from django.urls import path
from doctor_dev_catalogue.views import ddc_form, ddc_history, ddc_edit, ddc_delete

urlpatterns = [
    path('form/', ddc_form, name='ddc_form'),
    path('history/', ddc_history, name='ddc_history'),
    path('edit/<int:pk>/', ddc_edit, name='ddc_edit'),
    path('delete/<int:pk>/', ddc_delete, name='ddc_delete'),
]
