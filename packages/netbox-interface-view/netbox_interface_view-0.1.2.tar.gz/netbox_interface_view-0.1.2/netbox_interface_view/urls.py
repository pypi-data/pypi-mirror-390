from django.urls import path
from . import views

urlpatterns = [
    path('device/<int:device_id>/grid/', views.InterfaceGridView.as_view(), name='interface_grid'),
]
