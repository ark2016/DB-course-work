from django.urls import path
from . import views

app_name = 'foxapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/stats/', views.stats_api, name='stats_api'),
] 