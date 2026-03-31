from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('constellations/', views.constellation_list, name='constellation_list'),
    path('constellation/<int:pk>/', views.constellation_detail, name='constellation_detail'),
]