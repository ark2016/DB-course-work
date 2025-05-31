from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from .models import Survey, Image, Fox, Camera, SurveyImageInt, FoxImageInt, Location, ContactPerson


def dashboard(request):
    """Главная страница с дашбордом"""
    # Статистика
    surveys_count = Survey.objects.count()
    images_count = Image.objects.count()
    fox_count = Fox.objects.count()
    camera_count = Camera.objects.count()
    
    # Изображения с лисицами
    images_with_fox = Image.objects.filter(has_fox=True).count()
    images_without_fox = Image.objects.filter(has_fox=False).count()
    
    # Статистика по возрастным группам лисиц
    fox_by_age_group = Fox.objects.values('age_group').annotate(count=Count('fox_id'))
    
    # Последние изображения
    recent_images = Image.objects.all().order_by('-capture_date_time')[:8]
    
    # Получаем списки для выпадающих списков
    cameras = Camera.objects.all()
    locations = Location.objects.all()
    surveys = Survey.objects.all()
    
    context = {
        'surveys_count': surveys_count,
        'images_count': images_count,
        'fox_count': fox_count,
        'camera_count': camera_count,
        'images_with_fox': images_with_fox,
        'images_without_fox': images_without_fox,
        'fox_by_age_group': fox_by_age_group,
        'recent_images': recent_images,
        'cameras': cameras,
        'locations': locations,
        'surveys': surveys,
    }
    return render(request, 'foxapp/dashboard.html', context)


def upload_image(request):
    """Загрузка нового изображения"""
    if request.method == 'POST':
        # Получаем данные из формы
        file_name = request.POST.get('file_name')
        capture_date_time = request.POST.get('capture_date_time')
        has_fox = request.POST.get('has_fox') == 'true'
        camera_id = request.POST.get('camera')
        location_name = request.POST.get('location')
        survey_id = request.POST.get('survey')
        
        # Получаем файл изображения
        image_file = request.FILES.get('image_file')
        
        # Создаем новое изображение
        image = Image(
            file_name=file_name,
            capture_date_time=capture_date_time,
            has_fox=has_fox,
            size=image_file.size if image_file else 0,
            image_file=image_file
        )
        
        # Устанавливаем связи, если они указаны
        if camera_id:
            camera = get_object_or_404(Camera, camera_id=camera_id)
            image.camera = camera
        
        if location_name:
            location = get_object_or_404(Location, name_of_location=location_name)
            image.location = location
        
        # Сохраняем изображение
        image.save()
        
        # Если указано исследование, создаем связь
        if survey_id:
            survey = get_object_or_404(Survey, survey_id=survey_id)
            SurveyImageInt.objects.create(survey=survey, image=image)
            
        messages.success(request, f'Изображение "{file_name}" успешно загружено!')
        
        return redirect('foxapp:dashboard')
    
    # Если запрос не POST, перенаправляем на дашборд
    return redirect('foxapp:dashboard')


def stats_api(request):
    """API для получения статистики в JSON формате"""
    stats = {
        'surveys': Survey.objects.count(),
        'images': Image.objects.count(),
        'foxes': Fox.objects.count(),
        'cameras': Camera.objects.count(),
        'images_with_fox': Image.objects.filter(has_fox=True).count(),
        'survey_image_relations': SurveyImageInt.objects.count(),
        'fox_image_relations': FoxImageInt.objects.count(),
        'fox_by_sex': {
            'male': Fox.objects.filter(sex='M').count(),
            'female': Fox.objects.filter(sex='F').count(),
            'unknown': Fox.objects.filter(sex='U').count(),
        }
    }
    return JsonResponse(stats) 