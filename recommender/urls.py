from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about_page, name='about'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/', views.profile_management, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recommendations/generate/', views.generate_recommendations, name='generate_recommendations'),
    path('recommendations/programmes/', views.programme_recommendations, name='programme_recommendations'),
    path('recommendations/resources/', views.resource_recommendations, name='resource_recommendations'),
    path('programmes/<int:pk>/', views.programme_detail, name='programme_detail'),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
]
