# core/urls.py
from django.urls import path
from . import views
from appointments.views import booking, appointment_confirmation, history
from orders.views import mechanic_dashboard, order_detail, toggle_checklist, upload_photo
from vehicles.views import add_vehicle

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('booking/', booking, name='booking'),
    path('booking/confirmation/<int:appointment_id>/', appointment_confirmation, name='appointment_confirmation'),
    path('history/', history, name='history'),
    path('mechanic/', mechanic_dashboard, name='mechanic_dashboard'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/toggle-checklist/<int:item_id>/', toggle_checklist, name='toggle_checklist'),
    path('orders/upload-photo/<int:order_id>/', upload_photo, name='upload_photo'),
    path('vehicles/add/', add_vehicle, name='add_vehicle'),
]