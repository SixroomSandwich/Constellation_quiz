from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('constellations/', views.constellation_list, name='constellation_list'),
    path('constellation/<int:pk>/', views.constellation_detail, name='constellation_detail'),
    path('constellation/create/', views.constellation_create, name='constellation_create'),
    path('constellation/<int:pk>/edit/', views.constellation_edit, name='constellation_edit'),
    path('constellation/<int:pk>/delete/', views.constellation_delete, name='constellation_delete'),
    path('quiz/', views.quiz_question, name='quiz_question'),
    path('quiz/check/', views.quiz_check, name='quiz_check'),
    path('quiz/reset/', views.quiz_reset, name='quiz_reset'),
]