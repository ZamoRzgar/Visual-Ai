from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('detector/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('api/detect', views.detect_objects, name='detect_objects'),
]
