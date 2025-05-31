from django.urls import path
from . import views

app_name = 'foxapp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/stats/', views.stats_api, name='stats_api'),
    path('upload/', views.upload_image, name='upload_image'),
] 