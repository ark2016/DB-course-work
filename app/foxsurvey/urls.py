from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),

    # Маршруты вашего приложения (раскомментируйте и замените 'your_app' при необходимости)
    # path('', include('your_app.urls')),
]
