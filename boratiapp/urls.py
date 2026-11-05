from django.urls import path
from . import views, admin_views

urlpatterns = [
    # --- User (Guest) Routes ---
    path('', views.user_index, name='user_index'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('checkout/<int:room_id>/', views.checkout_view, name='checkout'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),

    # --- Admin Routes ---
    path('boraati-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('boraati-admin/rooms/', admin_views.room_management, name='admin_room_management'),
    path('boraati-admin/rooms/add/', admin_views.add_room, name='admin_add_room'),
    
    # Verification & Check-in (Receipt & National ID Search)
    path('boraati-admin/verifications/', admin_views.booking_verification, name='admin_booking_verification'),
    path('boraati-admin/check-in/<int:booking_id>/', admin_views.process_check_in, name='admin_process_check_in'),
    
    # Financials & Expenses
    path('boraati-admin/financials/', admin_views.financial_report, name='admin_financial_report'), # (Salphaaf ykn view dabalataa irratti qindeessuu)
    path('boraati-admin/payment/verify/<int:payment_id>/', admin_views.verify_payment, name='admin_verify_payment'),
    path('boraati-admin/expense/add/', admin_views.add_expense, name='admin_add_expense'),
    path('boraati-admin/floors/add/', admin_views.add_floor, name='admin_add_floor'),
]