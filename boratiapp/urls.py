from django.urls import path
from . import views, admin_views

urlpatterns = [
    # --- User (Guest) Routes ---
    path('', views.user_index, name='user_index'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('checkout/<int:room_id>/', views.checkout_view, name='checkout'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    #path('login/', views.user_login_view, name='user_login'),

    # --- Admin Routes ---
    path('admin-login/', admin_views.admin_login_view, name='admin_login'),
    path('boraati-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('boraati-admin/rooms/', admin_views.room_management, name='admin_room_management'),
    path('boraati-admin/rooms/add/', admin_views.add_room, name='admin_add_room'),
    path('signup/', admin_views.signup_view, name='signup'),
    path('admin-logout/', admin_views.admin_logout_view, name='admin_logout'),
    
    # Verification & Check-in (Receipt & National ID Search)
    path('boraati-admin/verifications/', admin_views.booking_verification, name='admin_booking_verification'),
    path('boraati-admin/check-in/<int:booking_id>/', admin_views.process_check_in, name='admin_process_check_in'),
    
    # Financials & Expenses
    path('boraati-admin/financials/', admin_views.financial_report, name='admin_financial_report'), # (Salphaaf ykn view dabalataa irratti qindeessuu)
    path('boraati-admin/payment/verify/<int:payment_id>/', admin_views.verify_payment, name='admin_verify_payment'),
    path('boraati-admin/expense/add/', admin_views.add_expense, name='admin_add_expense'),
    path('boraati-admin/floors/add/', admin_views.add_floor, name='admin_add_floor'),

    #edit room path
    path('admin-panel/rooms/', admin_views.admin_rooms_view, name='admin_rooms'),
    path('admin-panel/rooms/edit/<int:room_id>/', admin_views.admin_edit_room_view, name='admin_edit_room'),
    path('admin-panel/rooms/toggle-status/<int:room_id>/', admin_views.admin_toggle_room_status_view, name='admin_toggle_room_status'),
    path('admin-panel/rooms/delete/<int:room_id>/', admin_views.admin_delete_room_view, name='admin_delete_room'),

    path('about/', views.about_view, name='about_page'),
    path('contact/', views.contact_view, name='contact_page'),
    path('feedback/', views.feedback_view, name='feedback_page'),

    # Admin Inquiries & Feedback Management Panel
    path('boraati-admin/inquiries/', admin_views.admin_messages_view, name='admin_messages'),
    path('boraati-admin/feedback/toggle/<int:fb_id>/', admin_views.admin_toggle_feedback, name='admin_toggle_feedback'),
    path('boraati-admin/about/edit/', admin_views.admin_edit_about_view, name='admin_edit_about'),

    #link url
    path('boraati-admin/rooms/add-by-link/', admin_views.admin_add_room_by_link_view, name='admin_add_room_by_link'),
    path('login/', views.email_login_view, name='user_login'),
]