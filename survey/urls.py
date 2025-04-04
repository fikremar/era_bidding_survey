from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.survey_list, name='survey_list'),
    path('survey/<int:survey_id>/', views.survey_view, name='survey'),
    path('success/', views.survey_success, name='survey_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/', views.generate_pdf, name='generate_pdf'),
]