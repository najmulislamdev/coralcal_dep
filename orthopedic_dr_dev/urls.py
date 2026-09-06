from django.urls import path 
from orthopedic_dr_dev.views import anniversary, delete_orthopedic_dr

urlpatterns = [
    path('form/', anniversary, name='odd_form'),
    path('edit/<int:pk>/', anniversary, name='odd_edit'),
    path('del/<int:pk>/', delete_orthopedic_dr, name='odd_delete'),
]
