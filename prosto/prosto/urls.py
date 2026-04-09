# prosto/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Импорты views из приложений
from core import views as core_views
from accounts import views as accounts_views
from appointments import views as appointments_views
from orders import views as orders_views
from vehicles import views as vehicles_views
from services import views as services_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главная
    path('', core_views.home, name='home'),
    path('profile/', core_views.profile, name='profile'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', accounts_views.custom_logout, name='logout'),  # ← next_page='/'
    path('register/', accounts_views.register, name='register'),

    # Запись (клиент)
    path('booking/', appointments_views.booking, name='booking'),
    path('booking/confirmation/<int:appointment_id>/', appointments_views.appointment_confirmation,
         name='appointment_confirmation'),
    path('my-orders/', appointments_views.my_orders, name='my_orders'),
    path('order-status/<int:order_id>/', appointments_views.order_status, name='order_status'),

    # Механик
    path('mechanic/', orders_views.mechanic_dashboard, name='mechanic_dashboard'),
    path('order/<int:order_id>/', orders_views.order_detail, name='order_detail'),
    path('orders/toggle-checklist/<int:item_id>/', orders_views.toggle_checklist, name='toggle_checklist'),
    path('orders/upload-photo/<int:order_id>/', orders_views.upload_photo, name='upload_photo'),
    path('appointments/pending/', appointments_views.pending_appointments, name='pending_appointments'),
    path('appointments/confirm/<int:appointment_id>/', appointments_views.confirm_appointment, name='confirm_appointment'),
    path('orders/take/<int:order_id>/', orders_views.take_order, name='take_order'),
    path('orders/start/<int:order_id>/', orders_views.start_order, name='start_order'),

    # Автомобили
    path('vehicles/add/', vehicles_views.add_vehicle, name='add_vehicle'),

# Управление услугами (владелец)
    path('services/', services_views.service_list, name='service_list'),
    path('services/create/', services_views.service_create, name='service_create'),
    path('services/edit/<int:service_id>/', services_views.service_edit, name='service_edit'),
    path('services/delete/<int:service_id>/', services_views.service_delete, name='service_delete'),
    path('services/toggle/<int:service_id>/', services_views.service_toggle_active, name='service_toggle_active'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)