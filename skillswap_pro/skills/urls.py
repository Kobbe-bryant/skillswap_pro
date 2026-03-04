from django.urls import path
from skills import views

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Marketplace
    path('marketplace/', views.marketplace, name='marketplace'),
    
    # User Profile
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Matching
    path('matching/', views.matching_view, name='matching'),
    
    # Swap Requests
    path('send-request/<int:receiver_id>/', views.send_swap_request, name='send_swap_request'),
    path('accept-request/<int:request_id>/', views.accept_swap_request, name='accept_swap_request'),
    path('reject-request/<int:request_id>/', views.reject_swap_request, name='reject_swap_request'),
    path('complete-request/<int:request_id>/', views.complete_swap_request, name='complete_swap_request'),
    path('cancel-request/<int:request_id>/', views.cancel_swap_request, name='cancel_swap_request'),
    
    # Additional features
    path('notifications/', views.notifications_list, name='notifications'),
    path('rate/<int:swap_id>/', views.leave_rating, name='leave_rating'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    # lesson/simulator routes
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/join/', views.lesson_join, name='lesson_join'),
    path('lessons/<int:lesson_id>/simulator/', views.lesson_simulator, name='lesson_simulator'),
]
